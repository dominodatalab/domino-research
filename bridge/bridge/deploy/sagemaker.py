import logging
from typing import List, Dict, Set, Union, Any
from bridge.types import Model, ModelVersion, Artifact
from bridge.deploy import DeployTarget
import boto3  # type: ignore
from botocore.exceptions import (  # type: ignore
    ClientError,
    NoCredentialsError,
    NoRegionError,
)
from pprint import pformat
import os
import time

logger = logging.getLogger(__name__)


class SageMakerDeployTarget(DeployTarget):
    target_name = "sagemaker"
    execution_role = "bridge-sagemaker-execution"
    execution_role_policy_arn = (
        "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
    )
    sagemaker_name_prefix = "brdg"

    def __init__(self):
        if profile := os.environ.get("BRDG_DEPLOY_AWS_PROFILE"):
            logger.info(f"Using deploy AWS profile {profile}")
            session = boto3.Session(profile_name=profile)
        else:
            session = boto3.session.Session()

        self.region = session.region_name

        try:
            self.sagemaker_client = session.client("sagemaker")
            self.s3_client = session.client("s3")
            self.s3_resource = session.resource("s3")
            self.iam_client = session.client("iam")

            sts = session.client("sts")
            self.identity = sts.get_caller_identity()
            logger.debug(pformat(self.identity))
            self.account_id = self.identity["Account"]
            self.bucket_name = f"bridge-models-{self.account_id}-{self.region}"

            logger.info(
                f"SageMakerDeployTarget initialized for region {self.region}"
            )
        except NoRegionError as e:
            logger.error("No AWS Region set, cannot initialize.")
            raise e
        except NoCredentialsError as e:
            logger.error("No AWS Credentials, cannot initialize.")
            raise e

    @property
    def target_id(self) -> str:
        return self.account_id

    def list_models(self) -> List[Model]:
        endpoint_prefix = f"{self.sagemaker_name_prefix}-"

        endpoints: List[Dict[Any, Any]] = []

        # The set of states an endpoint can be in such that we consider
        # the endpoint to exist and represent a deployed model-stage-version(s)
        # States ommitted from this list are not states we should ever reach
        # and the code would not handle these. So we chose to ignore endpoints
        # in these states for now.
        states_considered_existant = [
            "Creating",
            "Updating",
            "SystemUpdating",
            "InService",
            "Failed",
        ]

        for state in states_considered_existant:
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
            endpoint_name = endpoint["EndpointName"]  # eg: brdg-modelA-Staging
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
                        version_id=self._version_from_sagemaker_model_name(
                            sagemaker_model_name=variant["ModelName"],
                            model_name=model_name,
                        ),  # eg: 1 from brdg-modelC-1
                    )
                    for variant in endpoint_config[
                        "ProductionVariants"
                    ]  # eg: brdg-modelA-1
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
        resource_prefix = f"{self.sagemaker_name_prefix}-"

        logger.info("Removing all Sagemaker Endpoints")
        endpoints = self.sagemaker_client.list_endpoints(
            MaxResults=100,  # handle pagination
            NameContains=resource_prefix,
        )["Endpoints"]

        if len(endpoints) > 0:
            endpoint_names = [e["EndpointName"] for e in endpoints]

            logger.info("Waiting for all Sagemaker Endpoints to be deletable")

            self._poll_endpoints_until_status(
                endpoint_names=endpoint_names,
                desired_status_set={"InService", "Failed"},
                allow_subset_to_match=True,
            )

            logger.info("All Sagemaker Endpoints are deletable")
            for endpoint_name in endpoint_names:
                # The API returns all that *contain* not those
                # that *start with* the prefix
                if endpoint_name.startswith(resource_prefix):
                    logger.info(
                        "Removing Sagemaker Endpoint"
                        + f"with name {endpoint_name}"
                    )
                    self.sagemaker_client.delete_endpoint(
                        EndpointName=endpoint_name
                    )
        else:
            logger.info("No endpoints found")

        logger.info("Removing all Sagemaker Endpoint Configs")
        endpoint_configs = self.sagemaker_client.list_endpoint_configs(
            MaxResults=100,  # handle pagination
            NameContains=resource_prefix,
        )["EndpointConfigs"]

        for endpoint_config in endpoint_configs:
            if (
                endpoint_config_name := endpoint_config["EndpointConfigName"]
            ).startswith(resource_prefix):
                logger.info(
                    "Removing Sagemaker Endpoint Config "
                    + f"with name {endpoint_config_name}"
                )
                self.sagemaker_client.delete_endpoint_config(
                    EndpointConfigName=endpoint_config_name
                )

        logger.info("Removing all Sagemaker Models")
        models = self.sagemaker_client.list_models(
            # NextToken='string',
            MaxResults=100,
            NameContains=resource_prefix,
        )["Models"]

        for model in models:
            if (model_name := model["ModelName"]).startswith(resource_prefix):
                logger.info(
                    "Removing Sagemaker Model " + f"with name {model_name}"
                )
                self.sagemaker_client.delete_model(ModelName=model_name)

        try:
            logger.info(f"Removing all items in S3 Bucket {self.bucket_name}")
            bucket_resource = self.s3_resource.Bucket(self.bucket_name)
            bucket_resource.objects.all().delete()

            logger.info(f"Removing S3 Bucket {self.bucket_name}")
            response = self.s3_client.delete_bucket(Bucket=self.bucket_name)
            logger.debug(pformat(response))
        except self.s3_client.exceptions.NoSuchBucket:
            logger.info("No bucket found.")
        except Exception as e:
            logger.exception(e)

        # Teardown IAM role policy
        try:
            RoleName = self.execution_role
            PolicyArn = self.execution_role_policy_arn
            logger.info(f"Removing Execution Role Policy {PolicyArn}")
            response = self.iam_client.detach_role_policy(
                RoleName=RoleName, PolicyArn=PolicyArn
            )
            logger.debug(pformat(response))
        except self.iam_client.exceptions.NoSuchEntityException:
            logger.info("No policy found.")
        except Exception as e:
            logger.exception(e)

        # Teardown IAM role
        try:
            RoleName = self.execution_role
            logger.info(f"Removing Execution Role {RoleName}")
            response = self.iam_client.delete_role(RoleName=RoleName)
            logger.debug(pformat(response))
        except self.iam_client.exceptions.NoSuchEntityException:
            logger.info("No role found.")
        except Exception as e:
            logger.exception(e)

    def init(self):
        # Create S3 Bucket ${ACCOUNT_ID}-${REGION}-bridge-models
        # This does not appear to cause errors when the bucket already exists.
        bucket = self.bucket_name
        logger.info(f"Creating artifact bucket {bucket} if not exist.")
        try:
            if self.region == "us-east-1":
                response = self.s3_client.create_bucket(
                    ACL="private",
                    Bucket=bucket,
                )
            else:
                response = self.s3_client.create_bucket(
                    ACL="private",
                    Bucket=bucket,
                    CreateBucketConfiguration={
                        "LocationConstraint": self.region
                    },
                )
            logger.debug(pformat(response))
        except self.s3_client.exceptions.BucketAlreadyOwnedByYou:
            logger.info("Found existing bucket.")

        # Create IAM Role
        RoleName = self.execution_role
        logger.info(
            f"Create SageMaker execution role {RoleName} if not exist."
        )
        try:
            response = self.iam_client.create_role(
                RoleName=RoleName,
                AssumeRolePolicyDocument="""{
    "Version": "2012-10-17",
    "Statement": {
        "Effect": "Allow",
        "Principal": {"Service": "sagemaker.amazonaws.com" },
        "Action": "sts:AssumeRole"
    }
}""",
            )
            logger.debug(response)
        except self.iam_client.exceptions.EntityAlreadyExistsException:
            logger.info("Found existing role.")

        # Attach Sagemaker Full Access Policy
        PolicyArn = self.execution_role_policy_arn
        logger.info(f"Attaching execution role policy: {PolicyArn}")
        response = self.iam_client.attach_role_policy(
            PolicyArn=PolicyArn,
            RoleName=RoleName,
        )
        logger.debug(response)

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
        endpoint_name = self._endpoint_name(model_name, stage)
        endpoint = self.sagemaker_client.describe_endpoint(
            EndpointName=endpoint_name
        )

        status = endpoint["EndpointStatus"]
        # Cannot update a model in the creating or updating states
        # We ignore and let the control loop request the update again
        # in a future iteration.
        if status in {"Creating", "Updating", "SystemUpdating"}:
            logger.warning(
                "Attempted to update endpoint in a non-updatable state. "
                + "Skipping update."
            )
            return

        # We choose to treat models in the failed state as valid
        # if their config is correct. This prevents an endless
        # recreate loop if something about the artifact/config is
        # causing a failure. This means we expect to see updates
        # to endpoints in the failed state (when the user changes
        # the config). However, we cannot literally update a failed
        # endpoint in SageMaker. So we delete the endpoint upon a config
        # change and then let the control loop handle recreating it with
        # the right config. We don't recreate here because it requires
        # blocking until the deletion finishes.
        elif status in {"Failed"}:
            logger.warning(
                "Attempted to update endpoint in a failed state. "
                + "Deleting endpoint to recreate with new config."
            )
            self._delete_endpoint(model_name, stage)
            return

        elif status in {"Deleting"}:
            logger.error("Attempted to update endpoint that was deleted.")
            return

        elif status in {"InService"}:
            self._new_endpoint_config(
                model_name, stage, version_ids, overwrite=True
            )

            try:
                self.sagemaker_client.update_endpoint(
                    EndpointName=endpoint_name,
                    EndpointConfigName=self._endpoint_config_name(
                        model_name, stage
                    ),
                    # overwrite variant props
                    RetainAllVariantProperties=False,
                )
            except ClientError as e:
                logging.error(e)
                raise e
        else:
            logger.error(
                f"Attempted to update endpoint in unexpected status {status}"
            )

    def _delete_endpoint(self, model_name: str, stage: str):
        self._delete_endpoint_config(model_name, stage)
        try:
            self.sagemaker_client.delete_endpoint(
                EndpointName=self._endpoint_name(model_name, stage)
            )
        except ClientError as e:
            logging.error(e)
            raise e

    def _poll_endpoints_until_status(
        self,
        endpoint_names: List[str],
        desired_status_set: Set[str],
        allow_subset_to_match: bool = False,
        max_wait_seconds: int = 20 * 60,
        polling_delay: int = 30,
    ):
        iters = max_wait_seconds // polling_delay

        for _ in range(iters):
            status_set: Set[str] = set()
            for endpoint_name in endpoint_names:
                status = self.sagemaker_client.describe_endpoint(
                    EndpointName=endpoint_name
                )["EndpointStatus"]
                status_set.add(status)

            if allow_subset_to_match:
                matches = status_set.issubset(desired_status_set)
            else:
                matches = status_set == desired_status_set

            if matches or (len(status_set) == 0):
                break
            else:
                logger.info(
                    f"Current Status Set {status_set}. "
                    + f"Desired Set {desired_status_set}. "
                    + f"Waiting {polling_delay}s."
                )
                time.sleep(polling_delay)

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

        InstanceType = os.environ.get(
            "BRDG_DEPLOY_AWS_INSTANCE_TYPE", "ml.t2.medium"
        )

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
                        "InstanceType": InstanceType,
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
                self.bucket_name,
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
                Bucket=self.bucket_name,
                Key=self._s3_subpath_for_version_artifact(
                    version
                ),  # path in the s3 bucket
            )
        except ClientError as e:
            logging.error(e)
            raise e

    def _create_sagemaker_model(self, version: ModelVersion):
        # TODO: better error handling
        # Handle rare case where model is deleted, endpoints
        # enters deleting state, no longer appears in list_models
        # and is then re-created, leading to an error due to name
        # conflict.
        try:
            execution_role_arn = (
                f"arn:aws:iam::{self.account_id}:role/{self.execution_role}"
            )
            self.sagemaker_client.create_model(
                ModelName=self._sagemaker_model_name_for_version(version),
                PrimaryContainer={
                    "Image": f"667552661262.dkr.ecr.{self.region}.amazonaws.com/bridge-mlflow-runtime:latest",  # noqa: E501
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
                ExecutionRoleArn=execution_role_arn,
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
        return f"{self.sagemaker_name_prefix}-{model_name}-{stage}"

    def _endpoint_config_name(self, model_name: str, stage: str) -> str:
        return f"{self.sagemaker_name_prefix}-{model_name}-{stage}"

    def _sagemaker_model_name_for_version(self, version: ModelVersion) -> str:
        return self._sagemaker_model_name(
            version.model_name, version.version_id
        )

    def _sagemaker_model_name(self, model_name: str, version_id: str) -> str:
        return "-".join([self.sagemaker_name_prefix, model_name, version_id])

    def _version_from_sagemaker_model_name(
        self, sagemaker_model_name: str, model_name: str
    ) -> str:
        model_version_prefix = (
            f"{self.sagemaker_name_prefix}-{model_name}-"  # eg: brdg-ModelA-
        )
        return sagemaker_model_name.removeprefix(model_version_prefix)

    def _s3_subpath_for_version_artifact(self, version: ModelVersion) -> str:
        return f"{version.model_name}/{version.version_id}/artifact.tar.gz"

    def _s3_path_for_version_artifact(self, version: ModelVersion) -> str:
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{self._s3_subpath_for_version_artifact(version)}"  # noqa: E501
