from typing import List, Dict, Set
from bridge.types import Model, ModelVersion, Artifact
from bridge.deploy import DeployTarget
import socket
import signal
import os
from subprocess import Popen
from collections import defaultdict
import logging
from pprint import pformat
import threading
from flask import Flask, request, Response
import requests

logger = logging.getLogger(__name__)


class LocalDeploymentProxy:
    def __init__(self, target):
        self.target = target
        self.app = Flask(__name__)
        self.app.add_url_rule(
            "/<model>/<stage>/<path:path>",
            view_func=self.proxy,
            methods=["POST"],
        )

    def proxy(self, model, stage, path):
        port = self.target.routes.get(model, {}).get(stage)

        if port is None:
            return 404

        resp = requests.request(
            method=request.method,
            url=f"http://localhost:{port}/{path}",
            headers={
                key: value for (key, value) in request.headers if key != "Host"
            },
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            params=dict(request.args),
        )

        excluded_headers = [
            "content-encoding",
            "content-length",
            "transfer-encoding",
            "connection",
        ]
        headers = [
            (name, value)
            for (name, value) in resp.raw.headers.items()
            if name.lower() not in excluded_headers
        ]

        response = Response(resp.content, resp.status_code, headers)
        return response

    def run(self):
        self.handle = threading.Thread(
            target=self.app.run, kwargs={"host": "0.0.0.0", "port": 3000}
        )
        self.handle.start()


class ModelDeployment:
    def __init__(self, model_version: ModelVersion, model_uri: str, port: int):
        path = f"{model_version.model_name}:{model_version.version_id}"

        stdout = open(f"{path}.stdout", "w")
        stderr = open(f"{path}.stderr", "w")

        env = {}
        if env_path := os.environ.get("PATH"):
            env["PATH"] = env_path
        if env_home := os.environ.get("HOME"):
            env["HOME"] = env_home

        self.port = port
        self.handle = Popen(
            [
                "mlflow",
                "models",
                "serve",
                "--model-uri",
                model_uri,
                "--port",
                str(port),
                "--host",
                "127.0.0.1",
            ],
            stdout=stdout,
            stderr=stderr,
            preexec_fn=os.setsid,
            env=env,
        )

    def destroy(self):
        os.killpg(os.getpgid(self.handle.pid), signal.SIGTERM)
        self.handle.wait()


class LocalDeployTarget(DeployTarget):
    target_name = "local"

    @property
    def target_id(self) -> str:
        return socket.gethostname()

    def list_models(self) -> List[Model]:
        mvs = list(self.running_models.keys())
        for mv in mvs:
            if self.running_models[mv].handle.poll() is not None:
                logger.info(f"Detected stopped model deployment: {mv}")
                del self.running_models[mv]

        result = []
        for model_name, d in self.routes.items():
            model = Model(name=model_name, versions={})
            for stage, port in d.items():
                for mv, md in self.running_models.items():
                    if port == md.port:
                        model.versions[stage] = set([mv])
                        break
            result.append(model)
        logger.info(result)
        return result

    def teardown(self):
        # TODO: Shutdown Flask
        self.routes = {}
        models = list(self.running_models.keys())
        for model in models:
            self.running_models[model].destroy()
            del self.running_models[model]

    def __init__(self):
        self.running_models: Dict[ModelVersion, ModelDeployment] = {}
        # model, stage, port
        self.routes: Dict[str, Dict[str, int]] = {}
        self.proxy = LocalDeploymentProxy(self)
        self.proxy.run()

    def init(self):
        pass

    def create_versions(self, new_versions: Dict[ModelVersion, Artifact]):
        for model_version, artifact in new_versions.items():
            if model_version in self.running_models:
                logger.warning(
                    f"Model version already deployed: {model_version}"
                )
                continue
            logger.info(f"Deploying version {model_version}")
            with socket.socket() as s:
                s.bind(("", 0))
                port = s.getsockname()[1]
            logger.info(f"Selected port {port}")
            model_dir = os.path.splitext(os.path.splitext(artifact.path)[0])[0]
            self.running_models[model_version] = ModelDeployment(
                model_version, model_dir, port
            )

    def update_version_stage(
        self,
        current_routing: Dict[str, Dict[str, Set[str]]],
        desired_routing: Dict[str, Dict[str, Set[str]]],
    ):
        self.routes = defaultdict(dict)
        for model, d in desired_routing.items():
            for stage, versions in d.items():
                for version in versions:
                    mv = ModelVersion(model, version)
                    if md := self.running_models.get(mv):
                        self.routes[model][stage] = md.port
                    else:
                        logger.warning(f"Unknown version: {mv}")
        logger.info(pformat(self.routes))

    def delete_versions(self, deleted_versions: Set[ModelVersion]):
        for model_version in deleted_versions:
            if model_version in self.running_models:
                logger.info(f"Deleting version {model_version}")
                self.running_models[model_version].destroy()
                del self.running_models[model_version]
