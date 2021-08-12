import logging
from typing import List, Dict
from regsync.types import Model, ModelVersion, Artifact, LATEST_STAGE_NAME
from regsync.registry import ModelRegistry
from regsync.util import compress
from mlflow.tracking import MlflowClient  # type: ignore
from mlflow.entities.model_registry import RegisteredModel  # type: ignore
import os

logger = logging.getLogger(__name__)


class Client(ModelRegistry):
    def __init__(self, uri: str, model_cache_path: str = "models"):
        registry_uri = os.environ.get("REGSYNC_MLFLOW_REGISTRY_URI")
        tracking_uri = os.environ.get("REGSYNC_MLFLOW_TRACKING_URI")

        logger.info(
            (
                f"Registry client initialized with resistry uri "
                f"'{registry_uri}' and tracking uri '{tracking_uri}'"
            )
        )
        self.client = MlflowClient(
            registry_uri=registry_uri, tracking_uri=tracking_uri
        )
        self.models: Dict[str, RegisteredModel] = {}
        self.model_cache_path = os.path.abspath(model_cache_path)

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
                if stage == "Archived":
                    continue
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

    def fetch_version_artifact(
        self, model_name: str, version: str
    ) -> Artifact:
        mv = self.client.get_model_version(model_name, version)
        logger.info(mv)
        directory = os.path.join(self.model_cache_path, model_name, version)
        os.makedirs(directory, exist_ok=False)
        path = self.client.download_artifacts(mv.run_id, "", directory)
        model_dir = os.listdir(directory)[0]
        outpath = compress(os.path.join(path, model_dir))
        return Artifact(outpath)
