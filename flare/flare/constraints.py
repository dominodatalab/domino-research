from dataclasses import dataclass
from typing import List, Optional


@dataclass
class NumericalConstraints:
    is_non_negative: bool


@dataclass
class StringConstraints:
    domains: List[str]


@dataclass
class DistributionConstraints:
    # 'Enabled' | 'Disabled'
    perform_comparison: str = "Enabled"
    comparison_threshold: float = 0.1
    # 'Simple' | 'Robust'
    comparison_method: str = "Simple"


@dataclass
class MonitoringConfig:
    distribution_constraints: DistributionConstraints
    # 'Enabled' | 'Disabled'
    evaluate_constraints: str = "Enabled"
    # 'Enabled' | 'Disabled'
    emit_metrics: str = "Enabled"
    datatype_check_threshold: float = 0.1
    domain_content_threshold: float = 0.1


@dataclass
class Feature:
    name: str
    inferred_type: str
    # denotes observed non-null value percentage
    completeness: float
    num_constraints: Optional[NumericalConstraints] = None
    string_constraints: Optional[StringConstraints] = None
    monitoringConfigOverrides: Optional[MonitoringConfig] = None


@dataclass
class Constraints:
    features: List[Feature]
    monitoring_config: MonitoringConfig
    version: int = 0
