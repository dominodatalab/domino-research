from dataclasses import dataclass
from typing import Dict, Set


@dataclass
class ModelVersion:
    model_name: str
    version_id: str
    location: str = None  # type: ignore

    # Note that 'location' field is excluded from comparison
    def __hash__(self):
        return hash((self.model_name, self.version_id))

    def __eq__(self, other):
        return (
            other.model_name == self.model_name
            and other.version_id == self.version_id
        )


@dataclass
class Model:
    name: str
    versions: Dict[str, Set[ModelVersion]]

    def unique_versions(self) -> Set[ModelVersion]:
        output = set([])
        for _, versions in self.versions.items():
            output.update(versions)
        return output


@dataclass
class Artifact:
    path: str
