from bridge.deploy.sagemaker import SageMakerDeployTarget
from bridge.types import Artifact, ModelVersion
from typing import Dict, Set
import pytest  # type: ignore
from botocore.exceptions import (  # type: ignore
    NoCredentialsError,
    NoRegionError,
)
import random
import string
import time
import os


try:
    SageMakerDeployTarget()
    aws_creds_present = True
except (NoRegionError, NoCredentialsError):
    aws_creds_present = False

artifact_relative_path = "../bridge/examples/mlflow_model/model.tar.gz"
artifact_path = os.path.abspath(artifact_relative_path)

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(TEST_DIR, os.pardir))
ARTIFACT_PATH = os.path.abspath(
    os.path.join(PROJECT_DIR, "examples/mlflow_model/model.tar.gz")
)
artifact = Artifact(ARTIFACT_PATH)

SETUP_WAIT_TIME = 10


@pytest.mark.skipif(not aws_creds_present, reason="no aws creds")
def test_sagemaker_update_handles_failed_endpoint():
    s = SageMakerDeployTarget()
    s.teardown()
    time.sleep(SETUP_WAIT_TIME)
    s.init()
    time.sleep(SETUP_WAIT_TIME)

    m1 = f"model-{''.join(random.choices(string.ascii_uppercase, k=8))}"

    m1_v1 = "1"
    m1_v2 = "2"

    stage_Prod = "Prod"

    s0: Dict[str, Dict[str, Set[str]]] = {}
    s1 = {m1: {stage_Prod: {m1_v1}}}
    s2 = {
        m1: {stage_Prod: {m1_v2}},
    }

    # Step 1 - create endpoint then delete model out from
    s.create_versions(
        {
            ModelVersion(m1, m1_v1): artifact,
            ModelVersion(m1, m1_v2): artifact,
        }
    )

    s.update_version_stage(s0, s1)

    # delete model out from under the endpoint so that it fails
    s.delete_versions({ModelVersion(m1, m1_v1)})

    s._poll_endpoints_until_status(
        endpoint_names=[
            s._endpoint_name(m1, stage_Prod),
        ],
        desired_status_set={"Failed"},
    )

    # Step 2 - attempt an update, expect model to get deleted
    s.update_version_stage(s1, s2)

    time.sleep(20)

    models_s1 = s.list_models()
    assert m1 not in models_s1

    # Step 3 - update again, with model deleted
    # expect model to be created in correct state
    s.update_version_stage({}, s2)
    print("Validating in s2 state")
    models_s2 = s.list_models()
    assert {m.name for m in models_s2}.issuperset({m1})
    for m in models_s2:
        if m.name == m1:
            assert m.versions[stage_Prod] == {ModelVersion(m1, m1_v2)}
    print("Validated in s2 state")

    # step 4
    s._poll_endpoints_until_status(
        endpoint_names=[
            s._endpoint_name(m1, stage_Prod),
        ],
        desired_status_set={"InService"},
    )
    s.teardown()


@pytest.mark.skipif(not aws_creds_present, reason="no aws creds")
def test_sagemaker_update_handles_creating_updating_status_endpoint():
    s = SageMakerDeployTarget()
    s.teardown()
    time.sleep(SETUP_WAIT_TIME)
    s.init()
    time.sleep(SETUP_WAIT_TIME)

    m1 = f"model-{''.join(random.choices(string.ascii_uppercase, k=8))}"

    m1_v1 = "1"
    m1_v2 = "2"
    m1_v3 = "3"

    stage_Prod = "Prod"

    s0: Dict[str, Dict[str, Set[str]]] = {}
    s1 = {m1: {stage_Prod: {m1_v1}}}
    s2 = {
        m1: {stage_Prod: {m1_v2}},
    }
    s3 = {
        m1: {stage_Prod: {m1_v3}},
    }

    # Step 1 - create endpoint
    s.create_versions(
        {
            ModelVersion(m1, m1_v1): artifact,
            ModelVersion(m1, m1_v2): artifact,
            ModelVersion(m1, m1_v3): artifact,
        }
    )

    s.update_version_stage(s0, s1)

    print("Validating s1 state is correct")
    models_s1 = s.list_models()
    assert {m.name for m in models_s1}.issuperset({m1})
    for m in models_s1:
        if m.name == m1:
            assert m.versions[stage_Prod] == {ModelVersion(m1, m1_v1)}
    print("Validated s1 state is correct")

    # Step 2 - update while state creating, expect state to remain unchanged
    s._poll_endpoints_until_status(
        endpoint_names=[
            s._endpoint_name(m1, stage_Prod),
        ],
        desired_status_set={"Creating"},
    )

    s.update_version_stage(s1, s2)

    print("Validating still in s1 state")
    models_s1 = s.list_models()
    assert {m.name for m in models_s1}.issuperset({m1})
    for m in models_s1:
        if m.name == m1:
            assert m.versions[stage_Prod] == {ModelVersion(m1, m1_v1)}
    print("Validated still in s1 state")

    # step 3 - wait for state to stabilize and update
    s._poll_endpoints_until_status(
        endpoint_names=[
            s._endpoint_name(m1, stage_Prod),
        ],
        desired_status_set={"InService"},
    )

    s.update_version_stage(s1, s2)
    print("Validating in s2 state")
    models_s2 = s.list_models()
    assert {m.name for m in models_s2}.issuperset({m1})
    for m in models_s2:
        if m.name == m1:
            assert m.versions[stage_Prod] == {ModelVersion(m1, m1_v2)}
    print("Validated in s2 state")

    # step 4 - update again before waiting to stabilize
    s._poll_endpoints_until_status(
        endpoint_names=[
            s._endpoint_name(m1, stage_Prod),
        ],
        desired_status_set={"Updating"},
    )
    s.update_version_stage(s2, s3)

    print("Validating still in s2 state")
    models_s2 = s.list_models()
    assert {m.name for m in models_s2}.issuperset({m1})
    for m in models_s2:
        if m.name == m1:
            assert m.versions[stage_Prod] == {ModelVersion(m1, m1_v2)}
    print("Validated still in s2 state")

    # step 5 - wait for state to stabilize from updating to inservice
    # then update
    s._poll_endpoints_until_status(
        endpoint_names=[
            s._endpoint_name(m1, stage_Prod),
        ],
        desired_status_set={"InService"},
    )

    s.update_version_stage(s2, s3)
    print("Validating in s3 state")
    models_s3 = s.list_models()
    assert {m.name for m in models_s3}.issuperset({m1})
    for m in models_s3:
        if m.name == m1:
            assert m.versions[stage_Prod] == {ModelVersion(m1, m1_v3)}
    print("Validated in s3 state")

    # step 6
    s._poll_endpoints_until_status(
        endpoint_names=[
            s._endpoint_name(m1, stage_Prod),
        ],
        desired_status_set={"InService"},
    )
    s.teardown()


@pytest.mark.skipif(not aws_creds_present, reason="no aws creds")
def test_sagemaker_creates_and_updates_endpoints():
    s = SageMakerDeployTarget()
    s.teardown()
    time.sleep(SETUP_WAIT_TIME)
    s.init()
    time.sleep(SETUP_WAIT_TIME)

    m1 = f"model-{''.join(random.choices(string.ascii_uppercase, k=8))}"
    m2 = f"model-{''.join(random.choices(string.ascii_uppercase, k=8))}"
    m3 = f"model-{''.join(random.choices(string.ascii_uppercase, k=8))}"

    m1_v1 = "1"
    m1_v2 = "2"
    m1_v3 = "3"
    m2_v1 = "1"
    m3_v1 = "1"

    stage_Prod = "Prod"
    stage_Staging = "Staging"
    stage_Latest = "Latest"

    s0: Dict[str, Dict[str, Set[str]]] = {}
    s1 = {
        m1: {stage_Prod: {m1_v1}, stage_Staging: {m1_v1}},
        m2: {stage_Prod: {m2_v1}},
    }
    s2 = {
        m1: {stage_Prod: {m1_v1, m1_v2}, stage_Latest: {m1_v3}},
        m3: {stage_Prod: {m3_v1}},
    }

    # Step 1
    s.create_versions(
        {
            ModelVersion(m1, m1_v1): artifact,
            ModelVersion(m2, m2_v1): artifact,
        }
    )

    s.update_version_stage(s0, s1)

    models_s1 = s.list_models()

    print("Validating s1 state is correct")
    assert {m.name for m in models_s1}.issuperset({m1, m2})
    for m in models_s1:
        if m.name == m1:
            assert m.versions[stage_Prod] == {ModelVersion(m1, m1_v1)}
            assert m.versions[stage_Staging] == {ModelVersion(m1, m1_v1)}
        if m.name == m2:
            assert m.versions[stage_Prod] == {ModelVersion(m2, m2_v1)}

    print("Validated s1 state is correct")

    # Step 2
    print("Polling until s1 state stabilizes")

    s._poll_endpoints_until_status(
        endpoint_names=[
            s._endpoint_name(m1, stage_Prod),
            s._endpoint_name(m1, stage_Staging),
            s._endpoint_name(m2, stage_Prod),
        ],
        desired_status_set={"InService"},
    )

    # Step 3
    s.create_versions(
        {
            ModelVersion(m1, m1_v2): artifact,
            ModelVersion(m1, m1_v3): artifact,
            ModelVersion(m3, m3_v1): artifact,
        }
    )

    s.update_version_stage(s1, s2)

    s.delete_versions({ModelVersion(m2, m2_v1)})

    print("Validating s2 state is correct")
    models_s2 = s.list_models()
    assert {m.name for m in models_s2}.issuperset({m1, m3})
    assert m2 not in {m.name for m in models_s2}
    for m in models_s2:
        if m.name == m1:
            assert m.versions[stage_Prod] == {
                ModelVersion(m1, m1_v1),
                ModelVersion(m1, m1_v2),
            }
            assert m.versions[stage_Latest] == {ModelVersion(m1, m1_v3)}
        if m.name == m3:
            assert m.versions[stage_Prod] == {ModelVersion(m3, m3_v1)}
    print("Validated s2 state is correct")

    # Step 4
    s._poll_endpoints_until_status(
        endpoint_names=[
            s._endpoint_name(m1, stage_Prod),
            s._endpoint_name(m1, stage_Latest),
            s._endpoint_name(m3, stage_Prod),
        ],
        desired_status_set={"InService"},
    )

    s.teardown()
