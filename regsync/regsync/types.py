from dataclasses import dataclass
from typing import Dict, Set


@dataclass
class ModelVersion:
    model_name: str
    # TODO: rename to version_id
    version: str

    def __hash__(self):
        return hash((self.model_name, self.version))


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


LATEST_STAGE_NAME = "Latest"

DEFAULT_MODEL_CACHE_PATH = ".brdg-models"
