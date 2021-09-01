import pandas as pd  # type: ignore
from typing import Optional, List
import traceback
import os
import logging
import json
from dacite import from_dict
from flare.statistics import Statistics
from flare.statistics import Feature as FeatureStatistics
from flare.constraints import Constraints
from flare.constraints import Feature as FeatureConstraint
from flare.alerting import (
    FeatureAlert,
    Alert,
    InferenceException,
    FeatureAlertKind,
    AlertWebhookTarget,
)

FLARE_STATISTICS_PATH_VAR = "FLARE_STATISTICS_PATH"
FLARE_CONSTRAINTS_PATH_VAR = "FLARE_CONSTRAINTS_PATH"

logger = logging.getLogger("flare")


class Flare(object):
    model_name: str
    constraints: Optional[Constraints]
    statistics: Optional[Statistics]
    feature_alerts: List[FeatureAlert]
    target: AlertWebhookTarget

    def __init__(
        self, model_name: str, x: pd.DataFrame, target: AlertWebhookTarget
    ):
        self.model_name = model_name
        self.target = target
        statistics_path = os.environ.get(
            FLARE_STATISTICS_PATH_VAR, "statistics.json"
        )
        try:
            with open(statistics_path, "r") as f:
                data = json.load(f)
            self.statistics = from_dict(data_class=Statistics, data=data)
            logger.debug(f"Loaded statistics baseline: {self.statistics}")

        except Exception as e:
            logger.exception(f"Could not load statistics baseline: {e}")
            self.statistics = None

        constraints_path = os.environ.get(
            FLARE_CONSTRAINTS_PATH_VAR, "constraints.json"
        )

        try:
            with open(constraints_path, "r") as f:
                data = json.load(f)
            self.constraints = from_dict(data_class=Constraints, data=data)
            logger.debug(f"Loaded constraints baseline: {self.constraints}")
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
        dtype_name = str(col.dtype)
        if constraint.inferred_type == "Fractional":
            if not dtype_name.startswith("float"):
                result.append(
                    FeatureAlert(
                        name=col.name,
                        kind=FeatureAlertKind.TYPE.value,
                    )
                )

        elif constraint.inferred_type == "Integral":
            if not (
                dtype_name.startswith("int") or dtype_name.startswith("uint")
            ):
                result.append(
                    FeatureAlert(
                        name=col.name,
                        kind=FeatureAlertKind.TYPE.value,
                    )
                )

        elif constraint.inferred_type == "String":
            if not (dtype_name == "string") or (
                dtype_name[:2] in {"<U", ">U", "=U"}
            ):
                types = set(map(type, col.dropna()))
                if types != {str}:
                    result.append(
                        FeatureAlert(
                            name=col.name,
                            kind=FeatureAlertKind.TYPE.value,
                        )
                    )

        return result

    def __enter__(self):
        pass

    def __exit__(self, type, value, tb):
        inference_exception = None
        if type is not None:
            logger.exception(
                f"Exception occured during model inference: {value}"
            )
            inference_exception = InferenceException(
                message=value,
                traceback="\n".join(
                    traceback.format_exception(type, value, tb)
                ),
            )

        alert = Alert(
            self.model_name, self.feature_alerts, inference_exception
        )

        if len(alert.features) > 0 or alert.exception is not None:
            self.target.send_alert(alert)
