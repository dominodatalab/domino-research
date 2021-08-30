from typing import List, Optional
from dataclasses import dataclass
from enum import Enum


class FeatureAlertKind(Enum):
    # Sample was more than x standard deviations from mean
    OUTLIER = "Outlier"
    # Sample was outside of lower or upper bounds
    BOUND = "Bound"
    # Sample was not the correct data type
    TYPE = "Type"
    # Sample was null and feature is non-nullable
    NULL = "Null"
    # Sample was negative and feature was non-negative
    NEGATIVE = "Negative"
    # Sample was not a valid variant of a categorical feature
    CATEGORICAL = "Categorical"


@dataclass
class FeatureAlert:
    # Feature Name
    name: str
    # See FeatureAlertKind.value
    kind: str


@dataclass
class InferenceException:
    message: str
    traceback: str


@dataclass
class Alert:
    model_name: str
    features: List[FeatureAlert]
    exception: Optional[InferenceException]
