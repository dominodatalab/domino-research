import os
import hashlib
from mixpanel import Mixpanel  # type: ignore
from typing import Dict, Union
import logging


class AnalyticsClient:
    SERVER_INIT_EVENT_NAME = "server_initialized"

    def __init__(self, checkpoint_hostname: str, logger: logging.Logger):
        self.logger = logger

        mp_api_key = os.environ.get("MIXPANEL_API_KEY")

        analytics_configured = bool(mp_api_key)  # false if None (unset) or ""

        analytics_opted_out = (
            os.environ.get("CHECKPOINT_ANALYTICS_OPT_OUT") is not None
        )

        self.analytics_enabled = analytics_configured and (
            not analytics_opted_out
        )

        if self.analytics_enabled:
            logger.info(
                "Analytics is ENABLED. "
                + "To opt out set CHECKPOINT_ANALYTICS_OPT_OUT=1 "
                + "in your shell environment."
            )
        else:
            logger.info("Analytics is DISABLED.")
            logger.debug(
                "Analytics disabled diagnosis: "
                + f"API key present: {analytics_configured}. "
                + f"Opt out: {analytics_opted_out}"
            )

        self.mp_client = Mixpanel(mp_api_key)

        self.checkpoint_hostname = checkpoint_hostname

    def track_server_init(self):
        self._track_event(
            self.checkpoint_hostname,
            self.SERVER_INIT_EVENT_NAME,
            {},
        )

    def _track_event(
        self,
        distinct_id: str,
        event_name: str,
        event_data: Dict[str, Union[str, int, float]],
    ):
        if self.analytics_enabled:
            anonymized_id = self._anonymize_id(distinct_id)
            self.mp_client.track(anonymized_id, event_name, event_data)
            self.logger.debug(
                f"Reporting analytics event: {event_name} {event_data}"
            )
        else:
            self.logger.debug(
                "Analytics disabled. "
                + f"Not reporting analytics event: {event_name} {event_data}."
            )

    def _anonymize_id(self, distinct_id: str) -> str:
        return hashlib.sha256(distinct_id.encode()).hexdigest()
