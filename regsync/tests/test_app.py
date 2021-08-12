from regsync.deploy.sagemaker import SageMakerDeployTarget
from regsync.types import Artifact, ModelVersion, Model
from typing import Dict, Set
import pytest
import boto3  # type: ignore
from botocore.exceptions import NoCredentialsError  # type: ignore


def test_sagemaker_deploy_target():
    try:
        sts = boto3.client("sts")
        sts.get_caller_identity()
    except NoCredentialsError:
        pytest.skip("No AWS Credentials, skipping sagemaker test")

    s = SageMakerDeployTarget()
    a_path = (
        "/Users/joshuabroomberg/work/Domino/domino-research"
        + "/regsync/examples/mlflow_model/model.tar.gz"
    )

    artifact = Artifact(a_path, "")

    import random
    import string

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
    import time

    while True:
        r1 = s.sagemaker_client.describe_endpoint(
            EndpointName=s._endpoint_name(m1, stage_Prod)
        )["EndpointStatus"]
        r2 = s.sagemaker_client.describe_endpoint(
            EndpointName=s._endpoint_name(m1, stage_Staging)
        )["EndpointStatus"]
        r3 = s.sagemaker_client.describe_endpoint(
            EndpointName=s._endpoint_name(m2, stage_Prod)
        )["EndpointStatus"]
        status_set = {r1, r2, r3}
        if status_set == {"InService"}:
            break
        else:
            print(f"Statuses {status_set}. Waiting 10s.")
            time.sleep(10)

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
    while True:
        r1 = s.sagemaker_client.describe_endpoint(
            EndpointName=s._endpoint_name(m1, stage_Prod)
        )["EndpointStatus"]
        r2 = s.sagemaker_client.describe_endpoint(
            EndpointName=s._endpoint_name(m1, stage_Latest)
        )["EndpointStatus"]
        r3 = s.sagemaker_client.describe_endpoint(
            EndpointName=s._endpoint_name(m3, stage_Prod)
        )["EndpointStatus"]
        status_set = {r1, r2, r3}
        if status_set == {"InService"}:
            break
        else:
            print(f"Statuses {status_set}. Waiting 10s.")
            time.sleep(10)

    s.teardown()
