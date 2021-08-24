import os
import hashlib
from mixpanel import Mixpanel  # type: ignore
from typing import Dict
from bridge.deploy import DeployTarget
import logging

logger = logging.getLogger(__name__)

# NOTE: client will throw an error if key is missing
analytics_optout = os.environ.get("BRIDGE_ANALYTICS_OPT_OUT")
mp_api_key = os.environ.get("MIXPANEL_API_KEY")
mp_client = Mixpanel(mp_api_key)

DEPLOY_INIT_EVENT_NAME = "deploy_client_initialized"
DEPLOY_DESTROY_EVENT_NAME = "deploy_client_destroyed"
MODEL_VERSIONS_CREATED_EVENT_NAME = "model_versions_created"
MODEL_VERSIONS_DELETED_EVENT_NAME = "model_versions_deleted"
MODEL_ROUTING_CREATED_EVENT_NAME = "model_routing_created"
MODEL_ROUTING_UPDATED_EVENT_NAME = "model_routing_updated"
MODEL_ROUTING_DELETED_EVENT_NAME = "model_routing_deleted"
CONTROL_LOOP_RAN_EVENT_NAME = "control_loop_ran"

DEPLOY_KIND_FIELD_NAME = "deploy_kind"
NUM_VERSIONS_FIELD_NAME = "num_versions"


def track_deploy_client_init(deploy_target: DeployTarget):
    track_event(
        deploy_target.target_id,
        DEPLOY_INIT_EVENT_NAME,
        {DEPLOY_KIND_FIELD_NAME: deploy_target.target_name},
    )


def track_deploy_client_destroy(deploy_target: DeployTarget):
    track_event(
        deploy_target.target_id,
        DEPLOY_DESTROY_EVENT_NAME,
        {DEPLOY_KIND_FIELD_NAME: deploy_target.target_name},
    )


def track_model_versions_created(
    deploy_target: DeployTarget, num_versions: int
):
    track_event(
        deploy_target.target_id,
        MODEL_VERSIONS_CREATED_EVENT_NAME,
        {
            DEPLOY_KIND_FIELD_NAME: deploy_target.target_name,
            NUM_VERSIONS_FIELD_NAME: str(num_versions),
        },
    )


def track_model_versions_deleted(
    deploy_target: DeployTarget, num_versions: int
):
    track_event(
        deploy_target.target_id,
        MODEL_VERSIONS_DELETED_EVENT_NAME,
        {
            DEPLOY_KIND_FIELD_NAME: deploy_target.target_name,
            NUM_VERSIONS_FIELD_NAME: str(num_versions),
        },
    )


def track_model_routing_created(deploy_target: DeployTarget):
    track_event(
        deploy_target.target_id,
        MODEL_ROUTING_CREATED_EVENT_NAME,
        {DEPLOY_KIND_FIELD_NAME: deploy_target.target_name},
    )


def track_model_routing_updated(deploy_target: DeployTarget):
    track_event(
        deploy_target.target_id,
        MODEL_ROUTING_UPDATED_EVENT_NAME,
        {DEPLOY_KIND_FIELD_NAME: deploy_target.target_name},
    )


def track_model_routing_deleted(deploy_target: DeployTarget):
    track_event(
        deploy_target.target_id,
        MODEL_ROUTING_DELETED_EVENT_NAME,
        {DEPLOY_KIND_FIELD_NAME: deploy_target.target_name},
    )


def track_control_loop_executed(
    deploy_target: DeployTarget,
    num_desired_models: int,
    num_current_models: int,
):
    track_event(
        deploy_target.target_id,
        CONTROL_LOOP_RAN_EVENT_NAME,
        {
            DEPLOY_KIND_FIELD_NAME: deploy_target.target_name,
            "num_desired_models": str(num_desired_models),
            "num_current_models": str(num_current_models),
        },
    )


def track_event(target_id: str, event_name: str, event_data: Dict[str, str]):
    if analytics_optout is None:
        anonymized_id = _anonymize_id(target_id)
        mp_client.track(anonymized_id, event_name, event_data)
        logger.info(f"Reporting analytics event: {event_name} {event_data}")
    else:
        logger.info(
            "Opt-out detected. Not reporting analytics event: " + event_name
        )


def _anonymize_id(target_id: str) -> str:
    return hashlib.md5(target_id.encode()).hexdigest()
