from dataclasses import dataclass
import enum


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
