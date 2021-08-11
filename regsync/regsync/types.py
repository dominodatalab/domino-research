from dataclasses import dataclass
from typing import Dict, Set


@dataclass
class ModelVersion:
    model_name: str
    version: str

    def __hash__(self):
        return hash(self.model_name + self.version)


@dataclass
class Model:
    name: str
    versions: Dict[str, Set[ModelVersion]]


@dataclass
class Artifact:
    path: str
    kind: str
