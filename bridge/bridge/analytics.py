import os
import hashlib
from mixpanel import Mixpanel  # type: ignore
from typing import Dict, Union
from bridge.deploy import DeployTarget
import logging

logger = logging.getLogger(__name__)


class AnalyticsClient:
    DEPLOY_INIT_EVENT_NAME = "deploy_client_initialized"
    DEPLOY_DESTROY_EVENT_NAME = "deploy_client_destroyed"
    CONTROL_LOOP_RAN_EVENT_NAME = "control_loop_ran"

    DEPLOY_KIND_FIELD_NAME = "deploy_kind"
    NUM_DEPLOYMENTS_FIELD_NAME = "num_deployments"
    NUM_DEPLOYMENTS_CREATED_FIELD_NAME = "num_deployments_created"
    NUM_DEPLOYMENTS_DELETED_FIELD_NAME = "num_deployments_deleted"
    EXECUTION_TIME = "execution_time"

    def __init__(self, deploy_target: DeployTarget):
        mp_api_key = os.environ.get("MIXPANEL_API_KEY")

        analytics_configured = bool(mp_api_key)  # false if None (unset) or ""

        analytics_opted_out = (
            os.environ.get("BRIDGE_ANALYTICS_OPT_OUT") is not None
        )

        self.analytics_enabled = analytics_configured and (
            not analytics_opted_out
        )

        if self.analytics_enabled:
            logger.info(
                "Analytics is ENABLED. "
                + "To opt out set BRIDGE_ANALYTICS_OPT_OUT=1 "
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

        self.deploy_target = deploy_target

    def track_deploy_client_init(self):
        self._track_event(
            self.deploy_target.target_id,
            self.DEPLOY_INIT_EVENT_NAME,
            {self.DEPLOY_KIND_FIELD_NAME: self.deploy_target.target_name},
        )

    def track_deploy_client_destroy(self):
        self._track_event(
            self.deploy_target.target_id,
            self.DEPLOY_DESTROY_EVENT_NAME,
            {self.DEPLOY_KIND_FIELD_NAME: self.deploy_target.target_name},
        )

    def track_control_loop_executed(
        self,
        num_deployments: int,
        num_deployments_created: int,
        num_deployments_deleted: int,
        execution_time: float,
    ):
        self._track_event(
            self.deploy_target.target_id,
            self.CONTROL_LOOP_RAN_EVENT_NAME,
            {
                self.DEPLOY_KIND_FIELD_NAME: self.deploy_target.target_name,
                self.NUM_DEPLOYMENTS_FIELD_NAME: num_deployments,
                self.NUM_DEPLOYMENTS_CREATED_FIELD_NAME: (
                    num_deployments_created
                ),
                self.NUM_DEPLOYMENTS_DELETED_FIELD_NAME: (
                    num_deployments_deleted
                ),
                self.EXECUTION_TIME: execution_time,
            },
        )

    def _track_event(
        self,
        target_id: str,
        event_name: str,
        event_data: Dict[str, Union[str, int, float]],
    ):
        if self.analytics_enabled:
            anonymized_id = self._anonymize_id(target_id)
            self.mp_client.track(anonymized_id, event_name, event_data)
            logger.debug(
                f"Reporting analytics event: {event_name} {event_data}"
            )
        else:
            logger.debug(
                "Analytics disabled. "
                + f"Not reporting analytics event: {event_name} {event_data}."
            )

    def _anonymize_id(self, target_id: str) -> str:
        return hashlib.sha256(target_id.encode()).hexdigest()
