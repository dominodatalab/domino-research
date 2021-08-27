from dataclass import dataclass, asdict
from abc import ABC, abstractmethod
import requests
from typing import Dict


@dataclass
class Alert:
    model_name: str = "HuggingNose"
    feature_name: str = "input_text"
    kind: str = "Type"


class AlertTarget(ABC):
    # NOTE (Josh): who should be responsible for retries?
    # If not this class, then this method needs to return
    # a success/failure state.
    @abstractmethod
    def send_alert(self, alert: Alert):
        pass


class SlackAlertTarget(AlertTarget):
    def __init__(self, webhook_path: str):
        # this is everything after slack.com/services
        # I.E: /XXXXX/XXXXXX/XXXXXXXXXXXXXXXXXXXX
        self.webhook_path = webhook_path

    def send_alert(self, alert: Alert):
        requests.post(
            f"https://hooks.slack.com/services{self.webhook_path}",
            data=self._format_alert(alert))

    def _format_alert(self, alert: Alert) -> Dict[str, str]:
        return {
            "text": (
                f"Model {alert.model_name}: "
                + f"Detected problem of kind {alert.kind}"
                + f"in feature {alert.feature_name}"
            )
        }

class ZapierAlertTarget(AlertTarget):
    def __init__(self, webhook_path: str):
        # this is everything after https://hooks.zapier.com/hooks/catch
        # I.E: /XXXXX/XXXXXX
        self.webhook_path = webhook_path

    def send_alert(self, alert: Alert):
        requests.post(
            f"https://hooks.zapier.com/services{self.webhook_path}",
            data=self._format_alert(alert))

    def _format_alert(self, alert: Alert) -> Dict[str, str]:
        return asdict(alert)
