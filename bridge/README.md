# Bridge

The easiest way to deploy from MLFlow to SageMaker

![build](https://github.com/dominodatalab/domino-research/actions/workflows/bridge.yml/badge.svg?branch=main)
[![Docker Repository on Quay](https://quay.io/repository/domino/bridge/status "Docker Repository on Quay")](https://quay.io/repository/domino/bridge)

## Quickstart

First, use `bridge init` to create the AWS resources that Bridge needs to operate.
Runing this command will create:

* An S3 bucket for model artifacts.
* An IAM role for Sagemaker execution, `bridge-sagemaker-execution`, (with Sagemaker Full Access policy).

This only needs to be run once for a given AWS account and region.
The snippet below assumes you have an `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in your environment
with sufficient permissions to create S3 bucks and the IAM role.

```
docker run -it \
    -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
    -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
    -e AWS_DEFAULT_REGION=${AWS_REGION} \
    quay.io/domino/bridge:latest init sagemaker
```

Next, start the Bridge server:

```
docker run -it \
    -e BRIDGE_MLFLOW_REGISTRY_URI=${MLFLOW_REGISTRY_URI} \
    -e BRIDGE_MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI} \
    -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
    -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
    -e AWS_DEFAULT_REGION=${AWS_REGION} \
    quay.io/domino/bridge:latest
```

That's it! Bridge will begin syncing tagged model versions from Mlflow to
Sagemaker! To stop syncing, simply exit the container process. If you want
to resume, re-run the same command.

## Cleanup

If you are done using Bridge in a given AWS account and region, you can run:

```
docker run -it \
    -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
    -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
    -e AWS_DEFAULT_REGION=${AWS_REGION} quay.io/domino/bridge:latest \
    destroy sagemaker
```

This will remove:

* All Bridge-created Sagemaker models and endpoints.
* The Bridge S3 model artifact bucket.
* The Bridge Sagemaker IAM role.

## Development

1. In this directory (`domino-research/bridge`): 

```bash
# Install as local package
pip install -e .
```

2. Next, configure any environment variables, most importantly AWS credentials
   and Mlflow tracking and registry URIs:

* `BRDG_DEPLOY_AWS_PROFILE`: AWS profile for Sagemaker deployer (if different from Mlflow backend).
* `BRDG_DEPLOY_AWS_INSTANCE_TYPE`: AWS instance type for Sagemaker endpoints (default ml.t2.medium).
* `LOG_LEVEL`: Customize log level (default INFO).
* `BRIDGE_MODEL_CACHE_PATH`: Path for caching model artifacts (default .brdg-models)
* `BRIDGE_SCAN_INTERVAL_S`: Control loop refresh interval (default 15s).
* `BRIDGE_MLFLOW_REGISTRY_URI`: Mlflow registry uri.
* `BRIDGE_MLFLOW_TRACKING_URI`: Mlflow tracking uri.

In addition, you can use any standard `boto3` or Mlflow environment variables.

3. Finally, run the control loop:

```bash
bridge init sagemaker
bridge run
```

Any changes you make to the code will be picked up only on a restart of `bridge run`.

## Linting / Testing

```
pip install -r requirements-dev.txt

# Type check
mypy bridge

# Lint
flake bridge

# Unit tests (only run when AWS credentials present and take 20+ minutes)
python -m pytest

# Automatically fix lints
black .
```

## Build Docker Image

```
docker build .
```
