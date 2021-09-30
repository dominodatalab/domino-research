from dataclasses import dataclass
from typing import Dict, Set, Optional


@dataclass
class ModelVersion:
    model_name: str
    version_id: str

    def __hash__(self):
        return hash((self.model_name, self.version_id))

    def __eq__(self, other):
        return (
            other.model_name == self.model_name
            and other.version_id == self.version_id
        )


@dataclass
class ModelEndpoint:
    version: ModelVersion
    location: Optional[str]

    def __hash__(self):
        return hash((self.version, self.location))


@dataclass
class Model:
    name: str
    versions: Dict[str, Set[ModelEndpoint]]  # stage -> (version, location)

    def unique_versions(self) -> Set[ModelVersion]:
        return {
            endpoint.version
            for endpoints in self.versions.values()
            for endpoint in endpoints
        }


@dataclass
class Artifact:
    path: str
