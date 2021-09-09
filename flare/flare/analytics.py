import os
import hashlib
from mixpanel import Mixpanel  # type: ignore
from typing import Dict, Union
from flare.constants import MIXPANEL_API_KEY
import logging
import uuid

logger = logging.getLogger(__name__)


class AnalyticsClient:
    BASELINE_CREATED_EVENT_NAME = "baseline_created"

    def __init__(self):
        mp_api_key = MIXPANEL_API_KEY

        analytics_configured = bool(mp_api_key)  # false if None (unset) or ""

        analytics_opted_out = (
            os.environ.get("FLARE_ANALYTICS_OPT_OUT") is not None
        )

        self.analytics_enabled = analytics_configured and (
            not analytics_opted_out
        )

        if self.analytics_enabled:
            logger.warning(
                "Flare Analytics ENABLED. "
                + "To opt out set FLARE_ANALYTICS_OPT_OUT=1 "
                + "in your environment."
            )
        else:
            logger.warning("Flare Analytics DISABLED.")
            logger.debug(
                "Analytics disabled diagnosis: "
                + f"API key present: {analytics_configured}. "
                + f"Opt out: {analytics_opted_out}"
            )

        self.mp_client = Mixpanel(mp_api_key)
        self.client_id = str(uuid.uuid4())

    def track_baseline_created(self):
        self._track_event(
            self.client_id,
            self.BASELINE_CREATED_EVENT_NAME,
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
            logger.debug(
                f"Reporting analytics event: {event_name} {event_data}"
            )
        else:
            logger.debug(
                "Analytics disabled. "
                + f"Not reporting analytics event: {event_name} {event_data}."
            )

    def _anonymize_id(self, distinct_id: str) -> str:
        return hashlib.sha256(distinct_id.encode()).hexdigest()
