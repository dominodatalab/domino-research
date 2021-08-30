from dataclass import dataclass, asdict
from abc import ABC, abstractmethod
import requests
from typing import Dict
import logging


logger = logging.getLogger("flare")


@dataclass
class Alert:
    model_name: str = "HuggingNose"
    feature_name: str = "input_text"
    kind: str = "Type"


class AlertWebhookTarget(ABC):
    @abstractmethod
    def _alert_webhook_url(self) -> str:
        pass

    @abstractmethod
    def _format_alert(self, alert: Alert) -> Dict[str, str]:
        pass

    def send_alert(self, alert: Alert):
        formatted_alert = self._format_alert(alert)
        logger.debug(formatted_alert)

        resp = requests.post(self._alert_webhook_url(), data=formatted_alert)

        if resp.ok:
            logger.info(f"Sent alert to {type(self).__name__}")
        else:
            logger.error(
                f"Failed to send alert to {type(self).__name__}. "
                + f"Code: {resp.status_code}. Body: {resp.text}")


class SlackAlertTarget(AlertWebhookTarget):
    def __init__(self, slack_webhook_path: str):
        # Everything after https://hooks.slack.com/services
        # FORMAT: /XXXXX/XXXXXX/XXXXXXXXXXXXXXXXXXXX
        self.slack_webhook_path = slack_webhook_path

    def _alert_webhook_url(self) -> str:
        return f"https://hooks.slack.com/services{self.slack_webhook_path}"

    def _format_alert(self, alert: Alert) -> Dict[str, str]:
        return {
            "text": (
                f"Model {alert.model_name}: "
                + f"Detected problem of kind {alert.kind}"
                + f"in feature {alert.feature_name}"
            )
        }


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
