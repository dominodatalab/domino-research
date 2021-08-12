import logging
from typing import List, Dict, Set, Union, Any
from regsync.types import Model, ModelVersion, Artifact
from regsync.deploy import DeployTarget
import boto3  # type: ignore
from botocore.exceptions import ClientError  # type: ignore


logger = logging.getLogger(__name__)


class SageMakerDeployTarget(DeployTarget):
    SAGEMAKER_NAME_PREFIX = "rs"
    S3_BUCKET_NAME = "regsync-artifacts"
    S3_BUCKET_REGION = "us-east-2"

    def __init__(self):
        logger.info("SageMaker DeployTarget client initialized")
        session = boto3.Session(profile_name="gambit-sandbox")
        self.sagemaker_client = session.client("sagemaker")
        self.s3_client = session.client("s3")

    def list_models(self) -> List[Model]:
        endpoint_prefix = f"{self.SAGEMAKER_NAME_PREFIX}-"

        endpoints: List[Dict[Any, Any]] = []
        for state in ["Creating", "Updating", "SystemUpdating", "InService"]:
            endpoints.extend(
                self.sagemaker_client.list_endpoints(
                    SortBy="Name",
                    SortOrder="Ascending",
                    MaxResults=100,  # handle pagination
                    # NextToken = "",  # handle pagination
                    NameContains=endpoint_prefix,
                    StatusEquals=state,
                )["Endpoints"]
            )

        output: Dict[str, Model] = {}

        for endpoint in endpoints:
            endpoint_name = endpoint["EndpointName"]  # eg: rs-modelA-Staging
            stage = endpoint_name.split("-")[-1]  # eg: Staging

            model_name = endpoint_name.removeprefix(
                endpoint_prefix
            ).removesuffix(
                f"-{stage}"
            )  # eg: modelA

            endpoint_config = self.sagemaker_client.describe_endpoint_config(
                EndpointConfigName=self._endpoint_config_name(
                    model_name, stage
                )
            )

            versions = set(
                [
                    ModelVersion(
                        model_name=model_name,
                        version=self._version_from_sagemaker_model_name(
                            sagemaker_model_name=variant["ModelName"],
                            model_name=model_name,
                        ),  # eg: 1 from rs-modelC-1
                    )
                    for variant in endpoint_config[
                        "ProductionVariants"
                    ]  # eg: rs-modelA-1
                ]
            )

            if model := output.get(model_name):
                model.versions[stage] = versions
            else:
                output[model_name] = Model(
                    name=model_name,
                    versions={stage: versions},
                )

        return list(output.values())

    def teardown(self):
        resource_prefix = f"{self.SAGEMAKER_NAME_PREFIX}-"
        endpoints = self.sagemaker_client.list_endpoints(
            MaxResults=100,  # handle pagination
            NameContains=resource_prefix,
        )["Endpoints"]

        for endpoint in endpoints:
            if (endpoint_name := endpoint["EndpointName"]).startswith(
                resource_prefix
            ):
                self.sagemaker_client.delete_endpoint(
                    EndpointName=endpoint_name
                )

        endpoint_configs = self.sagemaker_client.list_endpoint_configs(
            MaxResults=100,  # handle pagination
            NameContains=resource_prefix,
        )["EndpointConfigs"]

        for endpoint_config in endpoint_configs:
            if (
                endpoint_config_name := endpoint_config["EndpointConfigName"]
            ).startswith(resource_prefix):
                self.sagemaker_client.delete_endpoint_config(
                    EndpointConfigName=endpoint_config_name
                )

        models = self.sagemaker_client.list_models(
            # NextToken='string',
            MaxResults=100,
            NameContains=resource_prefix,
        )["Models"]

        for model in models:
            if (model_name := model["ModelName"]).startswith(resource_prefix):
                self.sagemaker_client.delete_model(ModelName=model_name)

    def create_versions(self, new_versions: Dict[ModelVersion, Artifact]):
        for version, artifact in new_versions.items():
            self._upload_version_artifact(version, artifact)
            self._create_sagemaker_model(version)

    def delete_versions(self, deleted_versions: Set[ModelVersion]):
        for v in deleted_versions:
            self._delete_sagemaker_model(v)
            self._delete_version_artifact(v)

    def update_version_stage(
        self,
        current_routing: Dict[str, Dict[str, Set[str]]],
        desired_routing: Dict[str, Dict[str, Set[str]]],
    ):
        # Iterate through desired state and create/update endpoints
        # that are new/modified relative to current state.
        for (
            model_name,
            desired_model_stage_versions,
        ) in desired_routing.items():
            for (
                stage,
                desired_versions,
            ) in desired_model_stage_versions.items():

                # Check if the model appears in current state and if stage
                # is present
                if current_versions := current_routing.get(model_name, {}).get(
                    stage
                ):
                    # If model-stage exists, check if versions are correct
                    if current_versions != desired_versions:
                        # model-stage exists but versions are out-of-date.
                        self._update_endpoint(
                            model_name, stage, desired_versions
                        )
                else:
                    # model-stage is new, create model-stage endpoint
                    self._create_endpoint(model_name, stage, desired_versions)

        # Iterate through current state and remove endpoints for
        # model-stage pairs not in the desired state
        for (
            model_name,
            current_model_stage_versions,
        ) in current_routing.items():
            for (
                stage,
                current_versions,
            ) in current_model_stage_versions.items():
                if desired_routing.get(model_name, {}).get(stage) is None:
                    self._delete_endpoint(model_name, stage)

    def _create_endpoint(
        self, model_name: str, stage: str, version_ids: Set[str]
    ):
        self._new_endpoint_config(model_name, stage, version_ids)
        try:
            self.sagemaker_client.create_endpoint(
                EndpointName=self._endpoint_name(model_name, stage),
                EndpointConfigName=self._endpoint_config_name(
                    model_name, stage
                ),
            )
        except ClientError as e:
            logging.error(e)
            raise e

    def _update_endpoint(
        self, model_name: str, stage: str, version_ids: Set[str]
    ):
        self._new_endpoint_config(
            model_name, stage, version_ids, overwrite=True
        )
        try:
            self.sagemaker_client.update_endpoint(
                EndpointName=self._endpoint_name(model_name, stage),
                EndpointConfigName=self._endpoint_config_name(
                    model_name, stage
                ),
                RetainAllVariantProperties=False,  # overwrite variant props
                # TODO Consider smart default canary and auto-rollback using
                # DeploymentConfig options here
            )
        except ClientError as e:
            logging.error(e)
            raise e

    def _delete_endpoint(self, model_name: str, stage: str):
        self._delete_endpoint_config(model_name, stage)
        try:
            self.sagemaker_client.delete_endpoint(
                EndpointName=self._endpoint_name(model_name, stage)
            )
        except ClientError as e:
            logging.error(e)
            raise e

    def _new_endpoint_config(
        self,
        model_name: str,
        stage: str,
        version_ids: Set[str],
        overwrite=False,
    ):
        endpoint_config_name = self._endpoint_config_name(model_name, stage)

        # If overwrite, then attempt to delete and catch the resulting
        # error if the config is missing. Most efficient way to overwrite.
        if overwrite:
            try:
                self.sagemaker_client.delete_endpoint_config(
                    EndpointConfigName=endpoint_config_name
                )
            except ClientError as e:
                if e.response["Error"]["Message"].startswith(
                    "Could not find endpoint configuration"
                ):
                    logging.warn(
                        "_new_endpoint_config set to overwrite "
                        + "but config didn't exist."
                    )
                else:
                    logging.error(e)
                    raise e

        # create new config
        try:
            variants: List[Dict[str, Union[str, int]]] = []
            for version_id in version_ids:
                sagemaker_model_name = self._sagemaker_model_name(
                    model_name, version_id
                )
                variants.append(
                    {
                        "VariantName": sagemaker_model_name,
                        "ModelName": sagemaker_model_name,
                        "InitialInstanceCount": 1,
                        "InstanceType": "ml.t2.medium",
                        # will create a uniform split across all
                        # versions in this stage
                        "InitialVariantWeight": 1,
                    }
                )

            self.sagemaker_client.create_endpoint_config(
                EndpointConfigName=endpoint_config_name,
                ProductionVariants=variants,
            )
        except ClientError as e:
            logging.error(e)
            raise e

    def _delete_endpoint_config(self, model_name: str, stage: str):
        endpoint_config_name = self._endpoint_config_name(model_name, stage)
        try:
            self.sagemaker_client.delete_endpoint_config(
                EndpointConfigName=endpoint_config_name
            )
        except ClientError as e:
            logging.error(e)
            raise e

    def _upload_version_artifact(
        self, version: ModelVersion, artifact: Artifact
    ):
        # TODO: better error handling
        try:
            self.s3_client.upload_file(
                artifact.path,  # Absolute path to local file
                self.S3_BUCKET_NAME,
                self._s3_subpath_for_version_artifact(
                    version
                ),  # path in the s3 bucket
                # Ensure default SageMaker Executor Role has
                # access to object by tagging
                ExtraArgs={"Tagging": "SageMaker=true"},
            )
        except ClientError as e:
            logging.error(e)
            raise e

    def _delete_version_artifact(self, version: ModelVersion):
        # TODO: better error handling
        try:
            self.s3_client.delete_object(
                Bucket=self.S3_BUCKET_NAME,
                Key=self._s3_subpath_for_version_artifact(
                    version
                ),  # path in the s3 bucket
            )
        except ClientError as e:
            logging.error(e)
            raise e

    def _create_sagemaker_model(self, version: ModelVersion):
        # TODO: better error handling
        try:
            self.sagemaker_client.create_model(
                ModelName=self._sagemaker_model_name_for_version(version),
                PrimaryContainer={
                    # TODO: this shouldn't be hard coded
                    "Image": "667552661262.dkr.ecr.us-east-2.amazonaws.com/mlflow-pyfunc:1.19.0",  # noqa: E501
                    "ImageConfig": {
                        "RepositoryAccessMode": "Platform",
                    },
                    "Mode": "SingleModel",
                    "ModelDataUrl": self._s3_path_for_version_artifact(
                        version
                    ),
                    "Environment": {
                        "MLFLOW_DEPLOYMENT_FLAVOR_NAME": "python_function"
                    },
                },
                # TODO: this shouldn't be hard coded
                ExecutionRoleArn="arn:aws:iam::667552661262:role/kevin_sagemaker_execution",  # noqa: E501
                Tags=[],
            )
        except ClientError as e:
            logging.error(e)
            raise e

    def _delete_sagemaker_model(self, version: ModelVersion):
        # TODO: better error handling
        try:
            self.sagemaker_client.delete_model(
                ModelName=self._sagemaker_model_name_for_version(version)
            )
        except ClientError as e:
            logging.error(e)
            raise e

    # NOTE: we happen to use the same name for the endpoint
    # and endpoint config but this may not always be the case
    def _endpoint_name(self, model_name: str, stage: str) -> str:
        return f"{self.SAGEMAKER_NAME_PREFIX}-{model_name}-{stage}"

    def _endpoint_config_name(self, model_name: str, stage: str) -> str:
        return f"{self.SAGEMAKER_NAME_PREFIX}-{model_name}-{stage}"

    def _sagemaker_model_name_for_version(self, version: ModelVersion) -> str:
        return self._sagemaker_model_name(version.model_name, version.version)

    def _sagemaker_model_name(self, model_name: str, version_id: str) -> str:
        return "-".join([self.SAGEMAKER_NAME_PREFIX, model_name, version_id])

    def _version_from_sagemaker_model_name(
        self, sagemaker_model_name: str, model_name: str
    ) -> str:
        model_version_prefix = (
            f"{self.SAGEMAKER_NAME_PREFIX}-{model_name}-"  # eg: rs-ModelA-
        )
        return sagemaker_model_name.removeprefix(model_version_prefix)

    def _s3_subpath_for_version_artifact(self, version: ModelVersion) -> str:
        return f"{version.model_name}/{version.version}/artifact.tar.gz"

    def _s3_path_for_version_artifact(self, version: ModelVersion) -> str:
        return f"https://{self.S3_BUCKET_NAME}.s3.{self.S3_BUCKET_REGION}.amazonaws.com/{self._s3_subpath_for_version_artifact(version)}"  # noqa: E501


if __name__ == "__main__":
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
