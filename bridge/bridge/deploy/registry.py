from bridge.deploy.sagemaker import SageMakerDeployTarget
from bridge.deploy.local import LocalDeployTarget

DEPLOY_REGISTRY = {
    SageMakerDeployTarget.target_name: SageMakerDeployTarget,
    LocalDeployTarget.target_name: LocalDeployTarget,
}
