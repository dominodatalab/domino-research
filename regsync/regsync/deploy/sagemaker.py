import logging
from typing import List, Dict, Set
from regsync.types import Model, ModelVersion
from regsync.deploy import DeployTarget
import boto3  # type: ignore


logger = logging.getLogger(__name__)


class SageMakerDeployTarget(DeployTarget):
    SAGEMAKER_NAME_PREFIX = "regsync"

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

        output = []
        for endpoint in endpoint_data["Endpoints"]:
            endpoint_name = endpoint["EndpointName"]
            model_name = endpoint_name.removeprefix(endpoint_prefix)

            model_version_prefix = (
                f"{self.SAGEMAKER_NAME_PREFIX}-{model_name}-"
            )

            endpoint_config = self.client.describe_endpoint_config(
                EndpointConfigName=endpoint_name
            )

            versions = [
                ModelVersion(
                    version=variant["ModelName"].removeprefix(
                        model_version_prefix
                    ),
                    stages={variant["VariantName"]},
                )
                for variant in endpoint_config["ProductionVariants"]
            ]

            output.append(
                Model(
                    name=model_name,
                    versions=versions,
                )
            )

        return output

    def create_versions(self, new_versions: List[ModelVersion]):
        pass

    def update_version_stage(
        self, updated_versions: List[Dict[ModelVersion, Set[str]]]
    ):
        pass

    def delete_versions(self, deleted_versions: List[ModelVersion]):
        pass
