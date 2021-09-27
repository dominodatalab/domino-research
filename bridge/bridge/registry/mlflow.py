import logging
from typing import List, Dict, Optional
from bridge.types import Model, ModelVersion, Artifact
from bridge.constants import LATEST_STAGE_NAME
from bridge.constants import DEPLOY_URL_TAG
from bridge.constants import DEPLOY_STAGE_TAG
from bridge.registry import ModelRegistry
from bridge.util import compress
from mlflow.tracking import MlflowClient  # type: ignore
from mlflow.entities.model_registry import RegisteredModel  # type: ignore
import os

logger = logging.getLogger(__name__)


class Client(ModelRegistry):
    def __init__(self, model_cache_path: str):
        registry_uri = os.environ.get("BRIDGE_MLFLOW_REGISTRY_URI")
        tracking_uri = os.environ.get("BRIDGE_MLFLOW_TRACKING_URI")

        logger.info(
            (
                f"Registry client initialized with registry uri "
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
                            version_id=version.version,
                        )
                    ]
                )
            output.append(Model(name=model.name, versions=versions))
        return output

    def find_model_root(self, directory: str) -> Optional[str]:
        for path, dirs, files in os.walk(directory):
            for f in files:
                if f == "MLmodel":
                    return path
        return None

    def fetch_version_artifact(
        self, model_name: str, version: str
    ) -> Artifact:
        mv = self.client.get_model_version(model_name, version)
        logger.info(mv)
        directory = os.path.join(self.model_cache_path, model_name, version)
        outpath = os.path.join(directory, "model.tar.gz")
        if os.path.exists(directory):
            return Artifact(outpath)
        os.makedirs(directory, exist_ok=False)
        self.client.download_artifacts(mv.run_id, "", directory)
        if model_path := self.find_model_root(directory):
            logger.info(f"Found model path {model_path}.")
            compress(model_path, outpath)
            return Artifact(outpath)
        else:
            raise Exception(
                "Could not determine model root path. No MLmodel definition."
            )

    def tag_deployed_models(self, models: List[Model]):
        deployed_model_names = set[str]()
        deployed_versions = set[ModelVersion]()
        for model in models:
            for stage, versions in model.versions.items():
                for ver in versions:
                    deployed_model_names.add(ver.model_name)
                    deployed_versions.add(ver)
                    if ver.location is not None:
                        logger.info(
                            f"Tagging {ver.model_name}/{ver.version_id}"
                        )
                        self.client.set_model_version_tag(
                            ver.model_name,
                            ver.version_id,
                            DEPLOY_URL_TAG,
                            ver.location,
                        )
                        # TODO: DEPLOY_STAGE_TAG
        for model_name in deployed_model_names:
            for res in self.client.search_model_versions(
                "name='{}'".format(model_name)
            ):
                mv = ModelVersion(
                    model_name=res.name, version_id=res.version
                )  # For proper comparison
                if (mv not in deployed_versions) and (
                    (res.tags.get(DEPLOY_URL_TAG) is not None)
                    or (res.tags.get(DEPLOY_STAGE_TAG) is not None)
                ):
                    logger.info(f"Untagging {res.name}/{res.version}")
                    self.client.delete_model_version_tag(
                        res.name, res.version, DEPLOY_URL_TAG
                    )
                    self.client.delete_model_version_tag(
                        res.name, res.version, DEPLOY_STAGE_TAG
                    )

    def reset_tags(self):
        for model in self.client.list_registered_models():
            for res in self.client.search_model_versions(
                "name='{}'".format(model.name)
            ):
                if (res.tags.get(DEPLOY_URL_TAG) is not None) or (
                    res.tags.get(DEPLOY_STAGE_TAG) is not None
                ):
                    logger.info(f"Untagging {res.name}/{res.version}")
                    self.client.delete_model_version_tag(
                        res.name, res.version, DEPLOY_URL_TAG
                    )
                    self.client.delete_model_version_tag(
                        res.name, res.version, DEPLOY_STAGE_TAG
                    )
