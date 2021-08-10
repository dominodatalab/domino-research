import logging
import time
import os
import sys
from pprint import pformat

logger = logging.getLogger(__name__)


def main():
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    level = logging.getLevelName(LOG_LEVEL)
    logging.basicConfig(level=level)

    REGISTRY_URI = os.environ.get("APP_REGISTRY_URI")
    if REGISTRY_URI is None:
        logger.error("No APP_REGISTRY_URI specified.")
        sys.exit(1)

    REGISTRY_KIND = os.environ.get("APP_REGISTRY_KIND", "mlflow").lower()
    if REGISTRY_KIND == "mlflow":
        from regsync.registry.mlflow import Client

        registry_client = Client(REGISTRY_URI)
    else:
        logger.error(f"Unrecognized APP_REGISTRY_KIND '{REGISTRY_KIND}'")
        sys.exit(1)

    while True:
        try:
            logger.info("Reading models from registry")
            models = registry_client.list_models()
            logger.info(f"Found {len(models)} model(s).")
            logger.debug(pformat(models))
            for model in models:
                versions = registry_client.list_model_versions(model)
                logger.info(
                    f"Found {len(versions)} versions for model {model}"
                )
                logger.debug(pformat(versions))
        except Exception as e:
            logger.exception(e)
        time.sleep(15)
