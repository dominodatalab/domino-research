from monitor.runtime import Flare
import tempfile
import json
import pytest
from dataclasses import asdict
import os
import pandas as pd  # type: ignore
from monitor.runtime import FLARE_STATISTICS_PATH_VAR
import logging
from monitor.alerting import FeatureAlert


def generate_statistics():
    from monitor.statistics import (
        Dataset,
        StringStatistics,
        CommonStatistics,
        StringDistribution,
        CategoricalDistribution,
        NumericalStatistics,
        NumericalDistribution,
        KLLDistribution,
        KLLSketch,
        KLLSketchParameters,
        Statistics,
        Feature as FeatureStatistics,
    )

    float_feature = FeatureStatistics(
        name="float",
        inferred_type="Fractional",
        numerical_statistics=NumericalStatistics(
            common=CommonStatistics(num_present=1, num_missing=0),
            mean=1.0,
            sum=1.0,
            min=0.0,
            max=2.0,
            std_dev=1.0,
            distribution=NumericalDistribution(
                kll=KLLDistribution(
                    buckets=[],
                    sketch=KLLSketch(
                        parameters=KLLSketchParameters(
                            c=0.0,
                            k=0.0,
                        ),
                        data=[],
                    ),
                )
            ),
        ),
        string_statistics=None,
    )
    int_feature = FeatureStatistics(
        name="int",
        inferred_type="Integral",
        numerical_statistics=NumericalStatistics(
            common=CommonStatistics(num_present=1, num_missing=0),
            mean=1.0,
            sum=1.0,
            min=0.0,
            max=3.0,
            std_dev=1.0,
            distribution=NumericalDistribution(
                kll=KLLDistribution(
                    buckets=[],
                    sketch=KLLSketch(
                        parameters=KLLSketchParameters(
                            c=0.0,
                            k=0.0,
                        ),
                        data=[],
                    ),
                )
            ),
        ),
        string_statistics=None,
    )
    string_feature = FeatureStatistics(
        name="string",
        inferred_type="String",
        numerical_statistics=None,
        string_statistics=StringStatistics(
            distinct_count=1,
            distribution=StringDistribution(
                categorical=CategoricalDistribution(buckets=[])
            ),
            common=CommonStatistics(num_present=1, num_missing=0),
        ),
    )

    stats = Statistics(
        version=0,
        dataset=Dataset(item_count=1),
        features=[float_feature, int_feature, string_feature],
    )

    return stats


@pytest.fixture()
def statistics():
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w") as f:
        json.dump(asdict(generate_statistics()), f)
        f.flush()
        yield f.name


def test_bound(statistics):
    os.environ[FLARE_STATISTICS_PATH_VAR] = statistics
    level = logging.getLevelName("TRACE")
    logging.basicConfig(level=level)
    x = pd.DataFrame([[-1.0, 4, "3"]], columns=["float", "int", "string"])
    session = Flare(x)
    assert session.feature_alerts == [
        FeatureAlert(name="float", kind="Bound"),
        FeatureAlert(name="int", kind="Bound"),
    ]
