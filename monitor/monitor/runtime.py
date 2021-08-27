import pandas as pd  # type: ignore
from typing import Optional, List
import os
import logging
import json
from dacite import from_dict
from monitor.statistics import Statistics
from monitor.statistics import Feature as FeatureStatistics
from monitor.constraints import Constraints
from monitor.constraints import Feature as FeatureConstraint
from monitor.alerting import (
    FeatureAlert,
    Alert,
    InferenceException,
    FeatureAlertKind,
)

FLARE_STATISTICS_PATH_VAR = "FLARE_STATISTICS_PATH"
FLARE_CONSTRAINTS_PATH_VAR = "FLARE_CONSTRAINTS_PATH"
FLARE_NOTIFICATION_TOKEN_VAR = "FLARE_NOTIFICATION_TOKEN"

logger = logging.getLogger("flare")


class Flare(object):
    constraints: Optional[Constraints]
    statistics: Optional[Statistics]
    feature_alerts: List[FeatureAlert]

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

        self.feature_alerts: List[FeatureAlert] = []
        self.feature_alerts.extend(self._check_constraints(x))
        self.feature_alerts.extend(self._check_statistics(x))

    def _check_statistics(self, x: pd.DataFrame) -> List[FeatureAlert]:
        if self.statistics is None:
            logger.info("Skipping statistical checks.")
            return []

        result = []
        for feature in self.statistics.features:
            col = x[feature.name]
            result.extend(self._check_feature_statistics(feature, col))
        logger.info(f"Found {len(result)} statistical alerts.")
        return result

    def _check_feature_statistics(
        self, statistic: FeatureStatistics, col: pd.Series
    ) -> List[FeatureAlert]:
        result: List[FeatureAlert] = []

        outlier_cutoff = float(os.environ.get("FLARE_OUTLIER_CUTOFF", "4"))

        num_missing = None
        if numerical_statistic := statistic.numerical_statistics:
            # Check outlier
            if (
                (
                    abs(col - numerical_statistic.mean)
                    / numerical_statistic.std_dev
                )
                > outlier_cutoff
            ).any():
                result.append(
                    FeatureAlert(
                        name=col.name, kind=FeatureAlertKind.OUTLIER.value
                    )
                )

            # Check bound
            if (col < numerical_statistic.min).any() or (
                col > numerical_statistic.max
            ).any():
                result.append(
                    FeatureAlert(
                        name=col.name, kind=FeatureAlertKind.BOUND.value
                    )
                )

            num_missing = numerical_statistic.common.num_missing

        if string_statistic := statistic.string_statistics:
            num_missing = string_statistic.common.num_missing

        # Check null
        if num_missing is not None and num_missing == 0:
            if col.isnull().any():
                result.append(
                    FeatureAlert(
                        name=col.name, kind=FeatureAlertKind.NULL.value
                    )
                )

        return result

    def _check_constraints(self, x: pd.DataFrame) -> List[FeatureAlert]:
        if self.constraints is None:
            return []

        result = []
        for feature in self.constraints.features:
            col = x[feature.name]
            result.extend(self._check_feature_constraint(feature, col))
        return result

    def _check_feature_constraint(
        self, constraint: FeatureConstraint, col: pd.Series
    ) -> List[FeatureAlert]:
        result = []
        # Check non-negative
        if num_constraint := constraint.num_constraints:
            if num_constraint.is_non_negative:
                if (col < 0).any():
                    result.append(
                        FeatureAlert(
                            name=col.name, kind=FeatureAlertKind.NEGATIVE.value
                        )
                    )
        # Check categorical
        if string_constraint := constraint.string_constraints:
            if len(string_constraint.domains) > 0:
                if not col.isin(string_constraint.domains).all():
                    result.append(
                        FeatureAlert(
                            name=col.name,
                            kind=FeatureAlertKind.CATEGORICAL.value,
                        )
                    )

        # Check for type
        # TODO

        return result

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        inference_exception = None
        if type is not None:
            logger.exception(
                f"Exception occured during model inference: {value}"
            )
            inference_exception = InferenceException(
                message=value, traceback=traceback
            )

        alert = Alert(self.feature_alerts, inference_exception)

        if len(alert.features) > 0 or alert.exception is not None:
            pass
            # Emit alert


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
        dataset=Dataset(item_count=len(x)),
        features=[float_feature, int_feature, string_feature],
    )

    data = asdict(stats)
    with open("stats.json", "w") as f:
        json.dump(data, f)

    os.environ[FLARE_STATISTICS_PATH_VAR] = "stats.json"

    with Flare(x):
        pass
