from enum import Enum
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import requests  # type: ignore
from typing import Dict, List, Optional, Any
import logging


logger = logging.getLogger("flare")


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


class AlertWebhookTarget(ABC):
    @abstractmethod
    def _alert_webhook_url(self) -> str:
        pass

    @abstractmethod
    def _format_alert(self, alert: Alert) -> Dict[Any, Any]:
        pass

    def send_alert(self, alert: Alert):
        if (alert.exception is None) and (len(alert.features) == 0):
            logger.error("Alert has no exception/feature alerts. Not sending")
            return

        formatted_alert = self._format_alert(alert)
        logger.debug(formatted_alert)

        resp = requests.post(self._alert_webhook_url(), json=formatted_alert)

        if resp.ok:
            logger.info(f"Sent alert to {type(self).__name__}")
        else:
            logger.error(
                f"Failed to send alert to {type(self).__name__}. "
                + f"Code: {resp.status_code}. Body: {resp.text}"
            )


class SlackAlertTarget(AlertWebhookTarget):
    def __init__(self, slack_webhook_path: str):
        # Everything after https://hooks.slack.com/services
        # FORMAT: /XXXXX/XXXXXX/XXXXXXXXXXXXXXXXXXXX
        self.slack_webhook_path = slack_webhook_path

    def _alert_webhook_url(self) -> str:
        return f"https://hooks.slack.com/services{self.slack_webhook_path}"

    def _format_alert(self, alert: Alert) -> Dict[str, Any]:
        msg_structure: Dict[str, Any] = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Inference in model *{alert.model_name}* "
                        + "triggered Flare :sparkler: alerts:",
                    },
                },
            ]
        }

        if alert.exception is not None:
            msg_structure["blocks"].extend(
                [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "Runtime Exception",
                        },
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Message:* {alert.exception.message}\n"
                            + "*Full trace:*\n\n"
                            + f"{alert.exception.traceback[:20*1000]}",
                        },
                    },
                    {"type": "divider"},
                ]
            )

        if (num_alerts := len(alert.features)) > 0:
            msg_structure["blocks"].extend(
                [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"Input feature alerts ({num_alerts})",
                        },
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "\n".join(
                                [
                                    f"- Feature: {fa.name}. "
                                    + f"Alert kind: {fa.kind}"
                                    for fa in alert.features
                                ]
                            ),
                        },
                    },
                ]
            )

        return msg_structure


class ZapierAlertTarget(AlertWebhookTarget):
    def __init__(self, zapier_webhook_path: str):
        # this is everything after https://hooks.zapier.com/hooks/catch
        # FORMAT: /XXXXX/XXXXXX
        self.zapier_webhook_path = zapier_webhook_path

    def _alert_webhook_url(self) -> str:
        return f"https://hooks.zapier.com/services{self.zapier_webhook_path}"

    def _format_alert(self, alert: Alert) -> Dict[str, str]:
        return asdict(alert)


class CustomAlertTarget(AlertWebhookTarget):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def _alert_webhook_url(self) -> str:
        return self.webhook_url

    def _format_alert(self, alert: Alert) -> Dict[str, str]:
        return asdict(alert)
