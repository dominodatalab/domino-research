import pandas as pd  # type: ignore
from typing import Optional
import os
import logging
import json
from dacite import from_dict
from monitor.statistics import Statistics, Feature
from monitor.constraints import Constraints

FLARE_STATISTICS_PATH_VAR = "FLARE_STATISTICS_PATH"
FLARE_CONSTRAINTS_PATH_VAR = "FLARE_CONSTRAINTS_PATH"
FLARE_NOTIFICATION_TOKEN_VAR = "FLARE_NOTIFICATION_TOKEN"

logger = logging.getLogger("flare")


class Flare(object):
    constraints: Optional[Constraints]
    statistics: Optional[Statistics]

    def __init__(self, x: pd.DataFrame):
        if FLARE_NOTIFICATION_TOKEN_VAR not in os.environ:
            logger.warning("No notification token configured.")
            self.token = None
        else:
            self.token = os.environ[FLARE_NOTIFICATION_TOKEN_VAR]

        if FLARE_STATISTICS_PATH_VAR not in os.environ:
            logger.warning("No statistics file specified.")
            self.statistics = None
        else:
            path = os.environ[FLARE_STATISTICS_PATH_VAR]
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                self.statistics = from_dict(data_class=Statistics, data=data)
                logger.debug(f"Loaded statistics baseline: {self.statistics}")

            except Exception as e:
                logger.exception(f"Could not load statistics baseline: {e}")
                self.statistics = None

        if FLARE_CONSTRAINTS_PATH_VAR not in os.environ:
            logger.warning("No constraints file specified.")
            self.constraints = None
        else:
            path = os.environ[FLARE_CONSTRAINTS_PATH_VAR]
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                self.constraints = from_dict(data_class=Constraints, data=data)
                logger.debug(
                    f"Loaded constraints baseline: {self.constraints}"
                )
            except Exception as e:
                logger.exception(f"Could not load constraints baseline: {e}")
                self.constraints = None

        self.check_statistics(x)

    def check_statistics(self, x: pd.DataFrame):
        if self.statistics is None:
            return

        for feature in self.statistics.features:
            col = x[feature.name]
            self.check_feature_statistics(feature, col)

    def check_feature_statistics(self, feature: Feature, col: pd.Series):
        pass

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        if type is not None:
            logger.exception(
                f"Exception occured during model inference: {value}"
            )
        return True


if __name__ == "__main__":
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
    )
    from dataclasses import asdict

    level = logging.getLevelName("DEBUG")
    logging.basicConfig(level=level)

    x = pd.DataFrame([[1.0, 2, "3"]], columns=["float", "int", "string"])

    float_feature = Feature(
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
    int_feature = Feature(
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
    string_feature = Feature(
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
        dataset=Dataset(item_count=len(x)),
        features=[float_feature, int_feature, string_feature],
    )

    data = asdict(stats)
    with open("stats.json", "w") as f:
        json.dump(data, f)

    os.environ[FLARE_STATISTICS_PATH_VAR] = "stats.json"

    with Flare(x):
        pass
