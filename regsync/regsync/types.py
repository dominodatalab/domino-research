from dataclasses import dataclass, field
from typing import List, Set


@dataclass
class ModelVersion:
    version: str
    artifact_path: str
    artifact_type: str
    stages: Set[str] = field(default_factory=set)


@dataclass
class Model:
    name: str
    versions: List[ModelVersion]
