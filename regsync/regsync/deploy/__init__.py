from abc import ABC, abstractmethod
from typing import List, Dict, Set
from regsync.types import Model, ModelVersion


class DeployTarget(ABC):
    @abstractmethod
    def list_models(self) -> List[Model]:
        pass

    @abstractmethod
    def create_versions(self, new_versions: List[ModelVersion]):
        pass

    @abstractmethod
    def update_version_stage(
        self,
        current_routing: Dict[str, Dict[str, Set[str]]],
        desired_routing: Dict[str, Dict[str, Set[str]]],
    ):
        pass

    @abstractmethod
    def delete_versions(self, deleted_versions: List[ModelVersion]):
        pass
