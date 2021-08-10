from abc import ABC, abstractmethod
from typing import List
from regsync.types import Model, ModelVersion


class ModelRegistry(ABC):
    @abstractmethod
    def list_models(self) -> List[Model]:
        pass

    @abstractmethod
    def list_model_versions(self, model: Model) -> List[ModelVersion]:
        pass
