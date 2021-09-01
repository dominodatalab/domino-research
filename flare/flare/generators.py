from flare.constraints import (
    Constraints,
    NumericalConstraints,
    StringConstraints,
    MonitoringConfig,
    DistributionConstraints,
)
from flare.constraints import Feature as ConstraintFeature
from flare.statistics import (
    Statistics,
    Dataset,
    NumericalStatistics,
    StringStatistics,
    CommonStatistics,
)
from flare.statistics import Feature as StatisticsFeature

from flare.types import FeatureType
import pandas as pd  # type: ignore
from dataclasses import asdict
import json
import numpy as np

MAX_UNIQUES_THRESHOLD = 20
MAX_ROWS_FOR_OBJECT_TYPE_INFERENCE = 10 ** 5


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def baseline(df: pd.DataFrame):
    statistics = gen_statistics(df)
    constraints = gen_constraints(df)

    with open("constraints.json", "w") as f:
        json.dump(asdict(constraints), f, cls=NumpyEncoder)

    with open("statistics.json", "w") as f:
        json.dump(asdict(statistics), f, cls=NumpyEncoder)


def gen_statistics(df: pd.DataFrame) -> Statistics:
    statistics = Statistics(
        dataset=Dataset(len(df)),
        features=[
            _create_statistics_feature(feature_series)
            for name, feature_series in df.iteritems()
        ],
    )

    return statistics


def gen_constraints(df: pd.DataFrame) -> Constraints:
    features = [
        _create_constraints_feature(feature_series)
        for name, feature_series in df.iteritems()
    ]

    monitoring_config = MonitoringConfig(DistributionConstraints())

    constraints = Constraints(features, monitoring_config)

    return constraints


def _create_statistics_feature(feature_series: pd.Series) -> StatisticsFeature:
    feature_name = feature_series.name
    feature_type = _infer_feature_type(feature_series)

    feature = StatisticsFeature(
        name=feature_name, inferred_type=feature_type.value
    )

    # NOTE (Josh): this is duplicative of the completeness
    # constraint and also seems internally redundant?
    n_missing = feature_series.isna().sum()
    n_present = len(feature_series) - n_missing

    common = CommonStatistics(n_present, n_missing)

    if feature_type in {FeatureType.INTEGRAL, FeatureType.FRACTIONAL}:
        feature.numerical_statistics = NumericalStatistics(
            common=common,
            mean=feature_series.mean(),
            sum=feature_series.sum(),
            std_dev=feature_series.std(),
            min=feature_series.min(),
            max=feature_series.max(),
        )

    elif feature_type == FeatureType.STRING:
        feature.string_statistics = StringStatistics(
            common=common, distinct_count=len(feature_series.dropna().unique())
        )

    return feature


def _create_constraints_feature(
    feature_series: pd.Series,
) -> ConstraintFeature:
    feature_name = feature_series.name

    # 1. Infer type
    feature_type = _infer_feature_type(feature_series)

    # 2. Measure completeness
    n_missing = feature_series.isna().sum()
    feature_completeness = 1 - (n_missing / len(feature_series))

    feature = ConstraintFeature(
        name=feature_name,
        inferred_type=feature_type.value,
        completeness=feature_completeness,
    )

    # 3. Enrich with type-specific constraints
    if feature_type in {FeatureType.INTEGRAL, FeatureType.FRACTIONAL}:
        feature.num_constraints = NumericalConstraints(
            is_non_negative=bool(feature_series.min() >= 0)
        )

    elif feature_type == FeatureType.STRING:
        uniques = feature_series.dropna().unique()
        if len(uniques) <= MAX_UNIQUES_THRESHOLD:
            feature.string_constraints = StringConstraints(
                domains=list(uniques)
            )

    return feature


def _infer_feature_type(feature_series: pd.Series) -> FeatureType:
    dtype_name = str(feature_series.dtype)

    # {"int8", "int16", "int32", "int64", "intp"}
    # {"uint8", "uint16", "uint32", "uint64", "uintp"}
    if dtype_name.startswith("int") or dtype_name.startswith("uint"):
        feature_type = FeatureType.INTEGRAL

    # {"float16", "float32", "float64", "float96", "float128"}:
    elif dtype_name.startswith("float"):
        feature_type = FeatureType.FRACTIONAL

    # {"string", "<U16/32/...", ">U16/32/...", "=U16/32/..."}
    elif (dtype_name == "string") or (dtype_name[:2] in {"<U", ">U", "=U"}):
        feature_type = FeatureType.STRING

    elif dtype_name == "object":
        # Assume unknown type as object
        # dtype is assigned to mixed type
        # data
        feature_type = FeatureType.UNKNOWN

        # If dataset is small-ish, attempt to infer
        # if object dtype is actually strings
        if len(feature_series) <= MAX_ROWS_FOR_OBJECT_TYPE_INFERENCE:
            types = set(map(type, feature_series.dropna()))
            if types == {str}:
                feature_type = FeatureType.STRING

    else:
        # Bools, datetimes, etc are all treated as unknown
        feature_type = FeatureType.UNKNOWN

    return feature_type
