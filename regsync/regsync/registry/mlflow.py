import logging
from typing import List, Dict
from regsync.types import Model, ModelVersion
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
        self.models = {
            model.name: model for model in self.client.list_registered_models()
        }
        output = []
        for model in self.models.values():
            output.append(Model(name=model.name, versions=[]))
        return output

    def list_model_versions(self, model: Model) -> List[ModelVersion]:
        if reg_model := self.models.get(model.name):
            output = []
            for version in reg_model.latest_versions:
                output.append(
                    ModelVersion(
                        version=version.version,
                        artifact_type="",
                        artifact_path="",
                    )
                )
            return output
        return []
