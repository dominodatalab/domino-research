from checkpoint.types import ModelVersionStage, ModelVersion, Model
from mlflow.tracking import MlflowClient  # type: ignore
from mlflow.exceptions import RestException  # type: ignore

from typing import List, Optional
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
    def get_model_version_for_stage(
        self, model: Model, stage: ModelVersionStage
    ) -> Optional[ModelVersion]:
        pass

    @abstractmethod
    def get_model_version_stage(
        self, version: ModelVersion
    ) -> ModelVersionStage:
        pass

    @abstractmethod
    def transition_model_version_stage(
        self, version: ModelVersion, target_stage: ModelVersionStage
    ):
        pass

    @abstractmethod
    def list_stages_names(self) -> List[str]:
        pass

    @abstractmethod
    def stage_for_stage_name(self, stage_name: str) -> ModelVersionStage:
        pass


class MlflowRegistry(Registry):
    CHECKPOINT_TO_MLFLOW_STAGES = {
        ModelVersionStage.PRODUCTION: "Production",
        ModelVersionStage.STAGING: "Staging",
        ModelVersionStage.NONE: "None",
        ModelVersionStage.ARCHIVED: "Archived",
    }

    MLFLOW_TO_CHECKPOINT_STAGES = {
        "Production": ModelVersionStage.PRODUCTION,
        "Staging": ModelVersionStage.STAGING,
        "None": ModelVersionStage.NONE,
        "Archived": ModelVersionStage.ARCHIVED,
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
            model_name, self.MLFLOW_TO_CHECKPOINT_STAGES.keys()
        )

        if len(versions) >= 1:
            latest_version_number = max([int(v.version) for v in versions])

            return [
                ModelVersion(id=str(i), model_name=model_name)
                for i in range(1, latest_version_number + 1)
            ]
        else:
            return []

    def get_model_version_for_stage(
        self, model: Model, stage: ModelVersionStage
    ) -> Optional[ModelVersion]:
        versions = self.client.get_latest_versions(
            model.name, [self.CHECKPOINT_TO_MLFLOW_STAGES[stage]]
        )

        if (n_versions := len(versions)) > 1:
            e = RuntimeError(
                f"Expected 1 version for stage {stage}. Got {n_versions}"
            )
            logger.error(e)
            raise e
        elif n_versions == 0:
            return None
        else:
            return ModelVersion(
                model_name=model.name, id=str(versions[0].version)
            )

    def get_model_version_stage(
        self, version: ModelVersion
    ) -> ModelVersionStage:
        mlflow_version = self.client.get_model_version(
            version.model_name, int(version.id)
        )
        return self.MLFLOW_TO_CHECKPOINT_STAGES[mlflow_version.current_stage]

    def transition_model_version_stage(
        self, version: ModelVersion, target_stage: ModelVersionStage
    ):
        try:
            self.client.transition_model_version_stage(
                name=version.model_name,
                version=int(version.id),
                stage=self.CHECKPOINT_TO_MLFLOW_STAGES[target_stage],
                archive_existing_versions=True,
            )
        except RestException as e:
            logger.error(e)
            raise RegistryException(e)

    def list_stages_names(self) -> List[str]:
        return list(self.MLFLOW_TO_CHECKPOINT_STAGES.keys())

    def stage_for_stage_name(self, stage_name: str) -> ModelVersionStage:
        if stage_name in self.MLFLOW_TO_CHECKPOINT_STAGES:
            return self.MLFLOW_TO_CHECKPOINT_STAGES[stage_name]
        else:
            e = ValueError(f"Recieved unexpected stage name: {stage_name}")
            logger.error(e)
            raise e
