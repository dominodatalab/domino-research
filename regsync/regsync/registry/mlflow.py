import logging
from typing import List, Dict
from regsync.types import Model, ModelVersion, Artifact, LATEST_STAGE_NAME
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
            versions: Dict[str, set[ModelVersion]] = {}

            for version in model.latest_versions:
                stage = (
                    version.current_stage
                    if version.current_stage is not None
                    and version.current_stage != "None"
                    else LATEST_STAGE_NAME
                )
                versions[stage] = set(
                    [
                        ModelVersion(
                            model_name=model.name,
                            version=version.version,
                        )
                    ]
                )
            output.append(Model(name=model.name, versions=versions))
        return output

    def fetch_version(sefl, model_name: str, version: str) -> Artifact:
        pass
