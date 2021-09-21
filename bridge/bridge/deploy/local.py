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

logger = logging.getLogger(__name__)


class ModelDeployment:
    def __init__(self, model_version: ModelVersion, model_uri: str, port: int):
        path = f"{model_version.model_name}:{model_version.version_id}"

        stdout = open(f"{path}.stdout", "w")
        stderr = open(f"{path}.stderr", "w")

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
                "0.0.0.0",
            ],
            stdout=stdout,
            stderr=stderr,
            preexec_fn=os.setsid,
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
