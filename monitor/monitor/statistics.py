from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class KLLSketchParameters:
    c: float
    k: float


@dataclass
class KLLBucket:
    lower_bound: float
    upper_bound: float
    count: int


@dataclass
class KLLSketch:
    parameters: KLLSketchParameters
    data: List[List[float]]


@dataclass
class CategoryBucket:
    value: str
    count: int


@dataclass
class CategoricalDistribution:
    buckets: List[CategoryBucket]


@dataclass
class KLLDistribution:
    buckets: List[KLLBucket]
    sketch: KLLSketch


@dataclass
class StringDistribution:
    categorical: CategoricalDistribution


@dataclass
class NumericalDistribution:
    kll: KLLDistribution


@dataclass
class CommonStatistics:
    num_present: int
    num_missing: int


@dataclass
class NumericalStatistics:
    common: CommonStatistics
    mean: float
    sum: float
    std_dev: float
    min: float
    max: float

    # TODO: make this non-optional when we
    # decide to tackle sketches
    distribution: Optional[NumericalDistribution] = None


@dataclass
class StringStatistics:
    common: CommonStatistics
    distinct_count: int

    # TODO: make this non-optional when we
    # decide to tackle string distros
    distribution: Optional[StringDistribution] = None


@dataclass
class Feature:
    name: str
    inferred_type: str
    numerical_statistics: Optional[NumericalStatistics] = None
    string_statistics: Optional[StringStatistics] = None


@dataclass
class Dataset:
    item_count: int


@dataclass
class Statistics:
    dataset: Dataset
    version: int = 0
    features: List[Feature] = field(default_factory=list)
