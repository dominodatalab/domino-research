import logging
from typing import List, Dict, Set
from regsync.types import Model, ModelVersion
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

            model_version_prefix = (
                f"{self.SAGEMAKER_NAME_PREFIX}-{model_name}-"  # eg: rs-ModelA-
            )

            endpoint_config = self.client.describe_endpoint_config(
                EndpointConfigName=endpoint_name
            )

            versions = set(
                [
                    ModelVersion(
                        model_name=model_name,
                        version=variant["ModelName"].removeprefix(
                            model_version_prefix
                        ),  # eg: 1
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

    def create_versions(self, new_versions: List[ModelVersion]):
        pass

    def update_version_stage(
        self,
        current_routing: Dict[str, Dict[str, Set[str]]],
        desired_routing: Dict[str, Dict[str, Set[str]]],
    ):
        pass

    def delete_versions(self, deleted_versions: List[ModelVersion]):
        pass


s = SageMakerDeployTarget()
print(s.list_models())
