from abc import ABC, abstractmethod
from typing import List
from regsync.types import Model, ModelVersion


class DeployTarget(ABC):
    @abstractmethod
    def list_models(self) -> List[Model]:
        pass
