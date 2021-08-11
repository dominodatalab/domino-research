import logging
from typing import List, Dict, Set
from regsync.types import Model, ModelVersion, Artifact
from regsync.deploy import DeployTarget
import boto3  # type: ignore
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


class SageMakerDeployTarget(DeployTarget):
    SAGEMAKER_NAME_PREFIX = "rs"
    S3_BUCKET_NAME = "regsync-artifacts"
    S3_BUCKET_REGION = "us-east-2"

    def __init__(self):
        logger.info("SageMaker DeployTarget client initialized")
        session = boto3.Session(profile_name="gambit-sandbox")
        self.sagemaker_client = session.client("sagemaker")
        self.s3_client = session.client('s3')

    def list_models(self) -> List[Model]:
        endpoint_prefix = f"{self.SAGEMAKER_NAME_PREFIX}-"

        endpoint_data = self.sagemaker_client.list_endpoints(
            SortBy="Name",
            SortOrder="Ascending",
            MaxResults=100,
            # NextToken = "", # handle pagination
            NameContains=endpoint_prefix,
            StatusEquals="InService",  # handle creating etc
        )

        output: Dict[str, Model] = {}

        for endpoint in endpoint_data["Endpoints"]:
            endpoint_name = endpoint["EndpointName"]  # eg: rs-modelA-Staging
            endpoint_stage = endpoint_name.split("-")[-1]  # eg: Staging

            model_name = endpoint_name.removeprefix(
                endpoint_prefix
            ).removesuffix(
                f"-{endpoint_stage}"
            )  # eg: modelA

            endpoint_config = self.sagemaker_client.describe_endpoint_config(
                EndpointConfigName=endpoint_name
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
                model.versions[endpoint_stage] = versions
            else:
                output[model_name] = Model(
                    name=model_name,
                    versions={endpoint_stage: versions},
                )

        return list(output.values())

    def create_versions(self, new_versions: Dict[ModelVersion, Artifact]):
        for version, artifact in new_versions.items():
            self._upload_version_artifact(version, artifact)
            self._create_sagemaker_model(version)

    def update_version_stage(
        self,
        current_routing: Dict[str, Dict[str, Set[str]]],
        desired_routing: Dict[str, Dict[str, Set[str]]],
    ):
        pass

    def delete_versions(self, deleted_versions: Set[ModelVersion]):
        for v in deleted_versions:
            self._delete_sagemaker_model(v)
            self._delete_version_artifact(v)

    def _upload_version_artifact(self, version: ModelVersion, artifact: Artifact):
        # TODO: better error handling
        try:
            self.s3_client.upload_file(
                artifact.path,  # Absolute path to local file
                self.S3_BUCKET_NAME,
                self._s3_subpath_for_version_artifact(version),  # path in the s3 bucket
                # Ensure default SageMaker Executor Role has access to object by tagging
                ExtraArgs={"Tagging": "SageMaker=true"}
            )
        except ClientError as e:
            logging.error(e)
    
    def _delete_version_artifact(self, version: ModelVersion):
        # TODO: better error handling
        try:
            self.s3_client.delete_object(
                Bucket=self.S3_BUCKET_NAME,
                Key=self._s3_subpath_for_version_artifact(version) # path in the s3 bucket
            )
        except ClientError as e:
            logging.error(e)

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
                    "ModelDataUrl": self._s3_path_for_version_artifact(version),
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

    def _delete_sagemaker_model(self, version: ModelVersion):
        # TODO: better error handling
        try:
            self.sagemaker_client.delete_model(
                ModelName=self._sagemaker_model_name_for_version(version)
            )
        except ClientError as e:
            logging.error(e)

    def _sagemaker_model_name_for_version(self, version: ModelVersion) -> str:
        return "-".join(
            [self.SAGEMAKER_NAME_PREFIX, version.model_name, version.version]
        )

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

s = SageMakerDeployTarget()
# s.create_versions({
#     ModelVersion("modelE", "2"): Artifact("/Users/joshuabroomberg/work/Domino/domino-research/regsync/examples/mlflow_model/model.tar.gz", "")
# })
s.delete_versions({
    ModelVersion("modelD", "1")
})