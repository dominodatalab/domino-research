import enum
from typing import Dict, Any
from dataclasses import dataclass


class PromoteRequestStatus(enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    APPROVED = "approved"


class ModelVersionStage(enum.Enum):
    NONE = "none"
    ARCHIVED = "archived"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class Model:
    name: str


@dataclass
class ModelVersion:
    id: str
    model_name: str

    def __hash__(self):
        return hash((self.id, self.model_name))


@dataclass
class ModelVersionDetails:
    version: ModelVersion
    parameters: Dict[str, Any]
    metrics: Dict[str, Any]
    tags: Dict[str, str]
