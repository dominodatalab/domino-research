import logging
import time
import os
import sys
from pprint import pformat
from typing import List, Dict, Set
from regsync.types import Model, ModelVersion, Artifact
import shutil

logger = logging.getLogger(__name__)


def main():
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    level = logging.getLevelName(LOG_LEVEL)
    logging.basicConfig(level=level)

    MODEL_CACHE_PATH = os.environ.get("REGSYNC_MODEL_CACHE_PATH", "./models")
    shutil.rmtree(MODEL_CACHE_PATH, ignore_errors=True)

    REGISTRY_KIND = os.environ.get("REGSYNC_REGISTRY_KIND", "mlflow").lower()
    if REGISTRY_KIND == "mlflow":
        from regsync.registry.mlflow import Client

        registry_client = Client(MODEL_CACHE_PATH)
    else:
        logger.error(f"Unrecognized REGSYNC_REGISTRY_KIND '{REGISTRY_KIND}'")
        sys.exit(1)

    DEPLOY_KIND = os.environ.get("REGSYNC_DEPLOY_KIND", "sagemaker").lower()
    if DEPLOY_KIND == "sagemaker":
        from regsync.deploy.sagemaker import SageMakerDeployTarget

        deploy_client = SageMakerDeployTarget()
    else:
        logger.error(f"Unrecognized REGSYNC_REGISTRY_KIND '{REGISTRY_KIND}'")
        sys.exit(1)

    SCAN_INTERVAL = float(os.environ.get("REGSYNC_SCAN_INTERVAL_S", "15"))
    while True:
        try:
            logger.info("Reading models from registry")
            desired_models = registry_client.list_models()
            logger.info(f"Found {len(desired_models)} desired model(s).")
            logger.debug(pformat(desired_models))

            logger.info("Reading models from deploy target")
            current_models = deploy_client.list_models()
            logger.info(f"Found {len(current_models)} deployed model(s).")
            logger.debug(pformat(current_models))

            current_model_versions = {
                version
                for model in current_models
                for version in model.unique_versions()
            }
            desired_model_versions = {
                version
                for model in desired_models
                for version in model.unique_versions()
            }

            new_versions = desired_model_versions - current_model_versions
            new_versions_map: Dict[ModelVersion, Artifact] = {}
            for version in new_versions:
                logger.info(
                    (
                        f"Fetching {version.model_name}:{version.version} "
                        "artifact."
                    )
                )
                artifact = registry_client.fetch_version_artifact(
                    version.model_name, version.version
                )
                logger.info(artifact)
                new_versions_map[version] = artifact

            expired_versions = current_model_versions - desired_model_versions

            logger.debug(f"New model versions: {pformat(new_versions)}")
            logger.debug(
                f"Expired model versions: {pformat(expired_versions)}"
            )

            current_routing = routing_from_models(current_models)
            desired_routing = routing_from_models(desired_models)

            deploy_client.create_versions(new_versions_map)
            deploy_client.update_version_stage(
                current_routing, desired_routing
            )
            deploy_client.delete_versions(expired_versions)
            break
        except Exception as e:
            logger.exception(e)

        time.sleep(SCAN_INTERVAL)


def routing_from_models(models: List[Model]) -> Dict[str, Dict[str, Set[str]]]:
    return {
        model.name: {
            stage: {version.version for version in versions}
            for stage, versions in model.versions.items()
        }
        for model in models
    }
