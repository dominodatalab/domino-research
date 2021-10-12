from typing import List, Dict, Set
from bridge.types import Model, ModelVersion, Artifact, ModelEndpoint
from bridge.deploy import DeployTarget
import socket
import signal
import os
from subprocess import Popen
from collections import defaultdict
import logging
import threading
from flask import Flask, request, Response, abort
import requests  # type: ignore

requests.adapters.DEFAULT_RETRIES = 1

logger = logging.getLogger(__name__)
CONDA_LOCK_FILE = ".brdg_local.lock"

_ENDPOINT_ROOT = os.environ.get("BRIDGE_PUBLIC_URL", None)
_ENDPOINT_URL_PATTERN = "{0}/{1}/{2}/invocations"


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
            return abort(404)

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
            timeout=5,
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
        self.port = os.environ.get("PORT", 3000)
        self.handle = threading.Thread(
            target=self.app.run, kwargs={"host": "0.0.0.0", "port": self.port}
        )
        self.handle.start()


def destroy_failed_conda(model_dir):
    from mlflow.utils.conda import _get_conda_env_name  # type: ignore
    from mlflow.pyfunc import _load_model_env  # type: ignore
    from shutil import rmtree

    env = _load_model_env(model_dir)
    conda_env_path = f"{model_dir}/{env}"
    logger.info(f"Conda env path: {conda_env_path}")
    name = _get_conda_env_name(conda_env_path)
    logger.info(f"Destroying Conda environment {name}.")
    handle = Popen(
        [
            "conda",
            "env",
            "remove",
            "-n",
            name,
        ],
    )
    handle.wait()
    prefix = os.environ.get("CONDA_PREFIX", "/opt/conda")
    conda_env_dir = f"{prefix}/envs/{name}"
    logger.info(f"Conda Env Dir: {conda_env_dir}")
    rmtree(conda_env_dir, ignore_errors=True)
    logger.info(f"Done removing Conda env {handle.returncode}")


def prepare_conda_environment(model_dir, returns):
    from filelock import FileLock  # type: ignore
    from mlflow.utils.conda import get_or_create_conda_env  # type: ignore
    from mlflow.pyfunc import _load_model_env  # type: ignore

    env = _load_model_env(model_dir)
    conda_env_path = f"{model_dir}/{env}"
    lock = FileLock(CONDA_LOCK_FILE)
    logger.info(f"Obtaining lock {CONDA_LOCK_FILE}.")
    try:
        with lock:
            logger.info("Got lock.")
            get_or_create_conda_env(conda_env_path)
        returns[0] = 0
    except Exception as e:
        logger.exception(e)
        returns[0] = 1


class ModelDeployment:
    def __init__(self, model_version: ModelVersion, model_uri: str, port: int):
        self.model_version = model_version
        self.model_uri = model_uri
        self.serve_handle = None
        self.port = port
        self._install()

    def _install(self):
        # Install return code
        self.returns = [None]
        logger.info(f"Preparing Conda environment for {self.model_version}")
        self.install_handle = threading.Thread(
            target=prepare_conda_environment,
            args=(
                self.model_uri,
                self.returns,
            ),
        )
        self.install_handle.start()

    def check(self):
        # Check if currently installing
        if self.install_handle.is_alive() or self.returns[0] is None:
            logger.info(f"{self.model_version} installing...")
            return

        # Check if install complete and failed
        if self.returns[0]:
            logger.warning(f"{self.model_version} install failed.")
            destroy_failed_conda(self.model_uri)
            self._install()
            return

        # Check if install complete and success, but server not started
        if self.serve_handle is None:
            logger.info(f"Serving {self.model_version}")
            self._serve()
            return

        # Check if server process exited (restart)
        if self.serve_handle.poll() is not None:
            logger.info(
                f"Detected stopped model deployment {self.model_version}."
            )
            self._serve()

    def _serve(self):
        model_version = self.model_version
        path = f"{model_version.model_name}:{model_version.version_id}"
        stdout = open(f"{path}.stdout", "w")
        stderr = open(f"{path}.stderr", "w")

        env = {}
        if env_path := os.environ.get("PATH"):
            env["PATH"] = env_path
        if env_home := os.environ.get("HOME"):
            env["HOME"] = env_home

        self.serve_handle = Popen(
            [
                "mlflow",
                "models",
                "serve",
                "--model-uri",
                self.model_uri,
                "--port",
                str(self.port),
                "--host",
                "127.0.0.1",
            ],
            stdout=stdout,
            stderr=stderr,
            preexec_fn=os.setsid,
            env=env,
        )

    def destroy(self):
        if self.serve_handle is not None:
            os.killpg(os.getpgid(self.serve_handle.pid), signal.SIGTERM)
            self.serve_handle.wait()
            self.serve_handle = None


class LocalDeployTarget(DeployTarget):
    target_name = "localhost"

    def __init__(self):
        self.running_models: Dict[ModelVersion, ModelDeployment] = {}
        # model, stage, port
        self.routes: Dict[str, Dict[str, int]] = {}
        self.proxy = LocalDeploymentProxy(self)
        self.proxy.run()

    @property
    def target_id(self) -> str:
        return socket.gethostname()

    def list_models(self) -> List[Model]:
        # Run reconciliation loop for deployments
        mvs = list(self.running_models.keys())
        for mv in mvs:
            self.running_models[mv].check()

        result = []
        for model_name, d in self.routes.items():
            model = Model(name=model_name, versions={})
            for stage, port in d.items():
                for mv, md in self.running_models.items():
                    if port == md.port:
                        root = (
                            _ENDPOINT_ROOT
                            if _ENDPOINT_ROOT
                            else "http://localhost:" + str(self.proxy.port)
                        )
                        location = _ENDPOINT_URL_PATTERN.format(
                            root, model_name, stage
                        )
                        model.versions[stage] = set[ModelEndpoint](
                            [ModelEndpoint(mv, location)]
                        )
                        break
            result.append(model)
        return result

    def teardown(self):
        self.routes = {}
        models = list(self.running_models.keys())
        for model in models:
            self.running_models[model].destroy()
            del self.running_models[model]

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

    def delete_versions(self, deleted_versions: Set[ModelVersion]):
        for model_version in deleted_versions:
            if model_version in self.running_models:
                logger.info(f"Deleting version {model_version}")
                self.running_models[model_version].destroy()
                del self.running_models[model_version]
