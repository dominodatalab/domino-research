from checkpoint.types import ModelVersionStage, ModelVersion, Model
from mlflow.tracking import MlflowClient  # type: ignore
from mlflow.exceptions import RestException  # type: ignore

from typing import List
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class RegistryException(Exception):
    def __init__(self, cause: Exception):
        self.cause = cause


class Registry(ABC):
    @abstractmethod
    def list_models(self) -> List[Model]:
        pass

    @abstractmethod
    def list_model_versions(self, model_name: str) -> List[ModelVersion]:
        pass

    @abstractmethod
    def transition_model_version(
        self, version: ModelVersion, target_stage: ModelVersionStage
    ):
        pass


class MlflowRegistry(Registry):
    STAGE_MAPPING = {
        ModelVersionStage.PRODUCTION: "Production",
        ModelVersionStage.STAGING: "Staging",
        ModelVersionStage.NONE: "None",
        ModelVersionStage.ARCHIVED: "Archived",
    }

    def __init__(self, registry_uri, tracking_uri) -> None:
        self.client = MlflowClient(
            registry_uri=registry_uri, tracking_uri=tracking_uri
        )
        logger.info("Mlflow Registry initialized.")

    def list_models(self) -> List[Model]:
        models = [Model(m.name) for m in self.client.list_registered_models()]
        logger.info(f"Fetched {len(models)}Models from MLFlow.")
        return models

    def list_model_versions(self, model_name: str) -> List[ModelVersion]:
        versions = self.client.get_latest_versions(
            model_name, self.STAGE_MAPPING.values()
        )

        if len(versions) >= 1:
            latest_version_number = max([int(v.version) for v in versions])
            print(latest_version_number)

            return [
                ModelVersion(id=str(i), model_name=model_name)
                for i in range(1, latest_version_number + 1)
            ]
        else:
            return []

        return super().list_model_versions(model_name)

    def transition_model_version(
        self, version: ModelVersion, target_stage: ModelVersionStage
    ):
        try:
            self.client.transition_model_version_stage(
                name=version.model_name,
                version=int(version.id),
                stage=self.STAGE_MAPPING[target_stage],
                archive_existing_versions=True,
            )
        except RestException as e:
            logger.error(e)
            raise RegistryException(e)
