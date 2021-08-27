from typing import List, Optional
from dataclasses import dataclass


@dataclass
class FeatureAlert:
    # Feature Name
    name: str
    # 'Outlier' - Sample was more than x standard deviations from mean
    # 'Bound' - Sample was outside of lower or upper bounds
    # 'TypeMismatch' - Sample was not the correct data type
    # 'Null' - Sample was null and feature is non-nullable
    # 'Negative' - Sample was negative and feature was non-negative
    kind: str


@dataclass
class InferenceException:
    message: str
    traceback: str


@dataclass
class Alert:
    features: List[FeatureAlert]
    exception: Optional[InferenceException]
