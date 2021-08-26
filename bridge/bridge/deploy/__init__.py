from abc import ABC, abstractmethod
from typing import List, Dict, Set
from bridge.types import Model, ModelVersion, Artifact


class DeployTarget(ABC):
    @property
    @abstractmethod
    def target_name(self) -> str:
        pass

    @property
    @abstractmethod
    def target_id(self) -> str:
        pass

    @abstractmethod
    def list_models(self) -> List[Model]:
        pass

    @abstractmethod
    def teardown(self):
        pass

    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def create_versions(self, new_versions: Dict[ModelVersion, Artifact]):
        pass

    @abstractmethod
    def update_version_stage(
        self,
        current_routing: Dict[str, Dict[str, Set[str]]],
        desired_routing: Dict[str, Dict[str, Set[str]]],
    ):
        pass

    @abstractmethod
    def delete_versions(self, deleted_versions: Set[ModelVersion]):
        pass
