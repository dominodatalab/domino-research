import logging
from typing import List, Dict, Set
from regsync.types import Model, ModelVersion, Artifact
from regsync.deploy import DeployTarget
import boto3  # type: ignore


logger = logging.getLogger(__name__)


class SageMakerDeployTarget(DeployTarget):
    SAGEMAKER_NAME_PREFIX = "rs"

    def __init__(self):
        logger.info("SageMaker DeployTarget client initialized")
        session = boto3.Session(profile_name="gambit-sandbox")
        self.client = session.client("sagemaker")

    def list_models(self) -> List[Model]:
        endpoint_prefix = f"{self.SAGEMAKER_NAME_PREFIX}-"

        endpoint_data = self.client.list_endpoints(
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

            endpoint_config = self.client.describe_endpoint_config(
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
        for v in new_versions:
            self._create_sagemaker_model(v)

    def update_version_stage(
        self,
        current_routing: Dict[str, Dict[str, Set[str]]],
        desired_routing: Dict[str, Dict[str, Set[str]]],
    ):
        pass

    def delete_versions(self, deleted_versions: Set[ModelVersion]):
        for v in deleted_versions:
            self._delete_sagemaker_model(v)

    def _create_sagemaker_model(self, version: ModelVersion):
        # TODO: error handling
        self.client.create_model(
            ModelName=self._sagemaker_model_name_for_version(version),
            PrimaryContainer={
                # TODO: this shouldn't be hard coded
                "Image": "667552661262.dkr.ecr.us-east-2.amazonaws.com/mlflow-pyfunc:1.19.0",  # noqa: E501
                "ImageConfig": {
                    "RepositoryAccessMode": "Platform",
                },
                "Mode": "SingleModel",
                # TODO: this shouldn't be hard coded
                "ModelDataUrl": "https://s3.us-east-2.amazonaws.com/test-mlflow-deploy/test-mlflow-model-mccaucwptaa9hpnkbc4qwq/model.tar.gz",  # noqa: E501
                "Environment": {
                    "MLFLOW_DEPLOYMENT_FLAVOR_NAME": "python_function"
                },
            },
            # TODO: this shouldn't be hard coded
            ExecutionRoleArn="arn:aws:iam::667552661262:role/kevin_sagemaker_execution",  # noqa: E501
            Tags=[],
        )

    def _delete_sagemaker_model(self, version: ModelVersion):
        # TODO: error handling
        self.client.delete_model(
            ModelName=self._sagemaker_model_name_for_version(version)
        )

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
