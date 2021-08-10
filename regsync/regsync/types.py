from dataclasses import dataclass, field
from typing import List, Set


@dataclass
class ModelVersion:
    version: str
    stages: Set[str] = field(default_factory=set)


@dataclass
class Model:
    name: str
    versions: List[ModelVersion]


@dataclass
class Artifact:
    path: str
    kind: str
