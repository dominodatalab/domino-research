import logging
from typing import List, Dict, Optional
from bridge.types import Model, ModelVersion, Artifact, ModelEndpoint
from bridge.constants import LATEST_STAGE_NAME
from bridge.constants import DEPLOY_URL_TAG
from bridge.constants import DEPLOY_STATE_TAG
from bridge.registry import ModelRegistry
from bridge.util import compress
from mlflow.tracking import MlflowClient  # type: ignore
from mlflow.entities.model_registry import RegisteredModel  # type: ignore
from mlflow.entities.model_registry.model_version import (  # type: ignore
    ModelVersion as MlflowModelVersion,
)

import os
from enum import Enum

logger = logging.getLogger(__name__)


class DeploymentState(Enum):
    DEPLOYED = "DEPLOYED"  # Fully deployed to the target
    DEPLOYING = "UPDATING"  # In the process of being deployed to the target
    # Models that are being un-deployed are ignored


class Client(ModelRegistry):
    def __init__(self, model_cache_path: str):
        registry_uri = os.environ.get("BRIDGE_MLFLOW_URI")
        tracking_uri = os.environ.get("BRIDGE_MLFLOW_URI")

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
            versions: Dict[str, set[ModelEndpoint]] = {}

            for version in model.latest_versions:
                stage = (
                    version.current_stage
                    if version.current_stage is not None
                    and version.current_stage != "None"
                    else LATEST_STAGE_NAME
                )
                if stage == "Archived":
                    continue
                versions[stage] = set[ModelEndpoint](
                    [
                        ModelEndpoint(
                            ModelVersion(
                                model_name=model.name,
                                version_id=version.version,
                            ),
                            None,
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

    def tag_deployed_models(
        self, deployed_models: List[Model], registered_models: List[Model]
    ):
        # All versions of registered models currently found on MLflow
        all_mf_versions: List[MlflowModelVersion] = []

        # Collecting registered versions: ((name, version), stage)
        registered = set[(ModelVersion, str)]()  # type: ignore
        registered_to_mf = dict[ModelVersion, MlflowModelVersion]()
        for model in registered_models:
            for stage, endpoints in model.versions.items():
                for ep in endpoints:
                    ver = ep.version
                    registered.add((ver, stage))
                    query = "name='{}'".format(ver.model_name)
                    for mf_ver in self.client.search_model_versions(query):
                        all_mf_versions.append(mf_ver)
                        if (
                            mf_ver.name == ver.model_name
                            and mf_ver.version == ver.version_id
                        ):
                            registered_to_mf[ver] = mf_ver

        # Collecting & tagging deployed versions: ((name, version), stage)
        deployed = set[(ModelVersion, str)]()  # type: ignore
        for model in deployed_models:
            for stage, endpoints in model.versions.items():
                for ep in endpoints:
                    ver = ep.version
                    if (
                        ver,
                        stage,
                    ) in registered:
                        # Otherwise, the model is being un-deployed
                        deployed.add((ver, stage))
                        mf_ver = registered_to_mf[ver]
                        self.set_tag(
                            mf_ver,
                            DEPLOY_STATE_TAG,
                            DeploymentState.DEPLOYED.value,
                        )
                        if ep.location is not None:
                            self.set_tag(mf_ver, DEPLOY_URL_TAG, ep.location)

        # Untagging models that are not deployed
        for mf_ver in all_mf_versions:
            ver = ModelVersion(
                model_name=mf_ver.name, version_id=mf_ver.version
            )
            if ver not in {deployed_ver for deployed_ver, _ in deployed}:
                self.remove_tag(mf_ver, DEPLOY_URL_TAG)
                self.remove_tag(mf_ver, DEPLOY_STATE_TAG)

        # Tagging models that are being currently deployed
        for ver, _ in registered - deployed:
            mf_ver = registered_to_mf[ver]
            self.set_tag(
                mf_ver, DEPLOY_STATE_TAG, DeploymentState.DEPLOYING.value
            )
            self.remove_tag(mf_ver, DEPLOY_URL_TAG)

    def reset_tags(self):
        for model in self.client.list_registered_models():
            query = "name='{}'".format(model.name)
            for mod_ver in self.client.search_model_versions(query):
                self.remove_tag(mod_ver, DEPLOY_URL_TAG)
                self.remove_tag(mod_ver, DEPLOY_STATE_TAG)

    def set_tag(self, mf_ver: MlflowModelVersion, tag: str, value: str):
        current_value = mf_ver.tags.get(tag)
        if current_value != value:
            logger.info(
                f"Tagging {mf_ver.name}/{mf_ver.version}: {tag}={value}"
            )
            self.client.set_model_version_tag(
                mf_ver.name, mf_ver.version, tag, value
            )

    def remove_tag(self, mf_ver: MlflowModelVersion, tag: str):
        if mf_ver.tags.get(tag) is not None:
            logger.info(f"Untagging {mf_ver.name}/{mf_ver.version}: {tag}")
            self.client.delete_model_version_tag(
                mf_ver.name, mf_ver.version, tag
            )
