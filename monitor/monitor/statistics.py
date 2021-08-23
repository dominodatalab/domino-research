from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Statistics:
    dataset: Dataset
    version: int = 0
    features: List[Feature] = field(default_factory=list)


@dataclass
class Dataset:
    item_count: int


@dataclass
class Feature:
    name: str
    # 'Fractional' | 'Integral' | 'String'
    inferred_type: str
    numerical_statistics: Optional[NumericalStatistics]
    string_statistics: Optional[StringStatistics]


@dataclass
class NumericalStatistics:
    common: CommonStatistics
    mean: float
    sum: float
    std_dev: float
    min: float
    max: float
    distribution: NumericalDistribution


@dataclass
class StringStatistics:
    common: CommonStatistics
    distinct_count: int
    distribution: StringDistribution


@dataclass
class CommonStatistics:
    num_present: int
    num_missing: int


@dataclass
class NumericalDistribution:
    kll: KLLDistribution


@dataclass
class KLLDistribution:
    buckets: List[KLLBucket]
    sketch: KLLSketch


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
class KLLSketchParameters:
    c: float
    k: float


@dataclass
class StringDistribution:
    categorical: CategoricalDistribution


@dataclass
class CategoricalDistribution:
    buckets: List[CategoryBucket]


@dataclass
class CategoryBucket:
    value: str
    count: int
