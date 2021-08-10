from abc import ABC, abstractmethod
from typing import List
from regsync.types import Model, Artifact


class ModelRegistry(ABC):
    @abstractmethod
    def list_models(self) -> List[Model]:
        pass

    @abstractmethod
    def fetch_version(sefl, model_name: str, version: str) -> Artifact:
        pass
