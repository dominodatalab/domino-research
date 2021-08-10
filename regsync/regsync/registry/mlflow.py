import logging
from typing import List, Dict
from regsync.types import Model, ModelVersion, Artifact
from regsync.registry import ModelRegistry
from mlflow.tracking import MlflowClient  # type: ignore
from mlflow.entities.model_registry import RegisteredModel  # type: ignore

logger = logging.getLogger(__name__)


class Client(ModelRegistry):
    def __init__(self, uri: str):
        logger.info(f"Registry client initialized with uri '{uri}'")
        self.client = MlflowClient(registry_uri=uri)
        self.models: Dict[str, RegisteredModel] = {}

    def list_models(self) -> List[Model]:
        output = []
        for model in self.client.list_registered_models():
            versions = []
            for version in model.latest_versions:
                versions.append(
                    ModelVersion(
                        version=version.version,
                        stages=set([version.current_stage])
                        if version.current_stage is not None
                        and version.current_stage != "None"
                        else set([]),
                    )
                )
            output.append(Model(name=model.name, versions=versions))
        return output

    def fetch_version(sefl, model_name: str, version: str) -> Artifact:
        pass
