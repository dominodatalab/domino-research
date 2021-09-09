# :bridge_at_night: Bridge

The easiest way to deploy from MLflow to SageMaker 

![build](https://github.com/dominodatalab/domino-research/actions/workflows/bridge.yml/badge.svg?branch=main)
[![Docker Repository on Quay](https://quay.io/repository/domino/bridge/status "Docker Repository on Quay")](https://quay.io/repository/domino/bridge)

## Why Bridge

Bridge is designed to enable declarative model management, with your model registry as the source of truth.

- Data scientists manage the lifecycle of their models exclusively
through the built-for-purpose API and user interface of their 
Model registry. Stage labels (dev/staging/prod/etc) in the registry
become a declarative specification of which models should be deployed.

- DevOps and machine learning engineering teams use Bridge to
automate the often complex and frustrating management of SageMaker
resources. You manage Bridge, Bridge herds the AWS cats and manages
the repetitive wrapper code.

- Both teams can be confident that the models tagged in the
registry are the models being served, without having to dig
through git and CI logs or worrying about keeping things up to
date manually


## Quick Start

[Check out a 7 min demo of this Quick Start!](https://www.loom.com/share/c4498403c2794664a91be0d8e5119ecf)

This quickstart assumes that you already have an MLflow registry to work with.
If you do not have a registry, or would like to create a new registry for testing,
please follow our 5-min [guide to setting up MLflow locally](https://github.com/dominodatalab/domino-research/tree/main/guides/mlflow).

#### 1. Initialize Bridge

First, run the `init` command to create the AWS resources that Bridge needs to operate.
Running this command will create:

* An S3 bucket for model artifacts.
* An IAM role for Sagemaker execution, `bridge-sagemaker-execution`, (with Sagemaker Full Access policy).

This command only needs to be run once for a given AWS account and region.
The snippet below assumes you have an `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
in your environment with sufficient permissions to create S3 bucks and the IAM role.

```
docker run -it \
    -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
    -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
    -e AWS_DEFAULT_REGION=${AWS_REGION} \
    quay.io/domino/bridge:latest init sagemaker
```

#### 2. Run Bridge

Next, start the Bridge server and point it at your Mlflow registry.
This is done by setting environment variables named `MLFLOW_REGISTRY_URI` and `MLFLOW_TRACKING_URI`
with the correct values for your MLflow registry. 

```
docker run -it \
    -e BRIDGE_MLFLOW_REGISTRY_URI=${MLFLOW_REGISTRY_URI} \
    -e BRIDGE_MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI} \
    -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
    -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
    -e AWS_DEFAULT_REGION=${AWS_REGION} \
    quay.io/domino/bridge:latest
```

If you followed our [guide for setting up Mlflow locally](https://github.com/dominodatalab/domino-research/tree/main/guides/mlflow), then you should configure your environment
using the code snippets below:

For Linux:
```
export MLFLOW_REGISTRY_URI=http://localhost:5000
export MLFLOW_TRACKING_URI=http://localhost:5000
```

For macOS:
```
export MLFLOW_REGISTRY_URI=http://host.docker.internal:5000
export MLFLOW_TRACKING_URI=http://host.docker.internal:5000
```

#### 3. See the results

That's it! Bridge will begin syncing model versions from MlFlow to
Sagemaker! By default, it will sync versions assigned to Production and
Staging as well as the most recent version auto-tagged as `Latest`.

If you push a new version to a model in your registry, you will see
the `Latest` endpoint for that model create/update in SageMaker with that
version. If you then tag that version as `Staging` it will create/update the
`Staging` endpoint for the model with the version. Welcome to RegistryOps.

To stop syncing, simply exit the container process. If you want
to resume, re-run the same command above.

**Note:** Bridge deploys the *models* in MLflow (not runs).
Models must use the MLflow [storage format](https://www.mlflow.org/docs/latest/models.html#storage-format).
I.E., the model must have a valid [MLmodel](https://www.mlflow.org/docs/latest/models.html)
file in the artifacts stored in each of its versions. This is
usually achieved by calling `mlflow.<framework>.log_model`
or using the `create_model_version` command with appropriate inputs.

## Cleanup

If you are done using Bridge in a given AWS account and region, you can run
the command below to remove all traces of Bridge. This will **delete all
the resources** managed by Bridge but no resources from your registry.

```
docker run -it \
    -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
    -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
    -e AWS_DEFAULT_REGION=${AWS_REGION} quay.io/domino/bridge:latest \
    destroy sagemaker
```

The command will remove:

* All Bridge-created Sagemaker models and endpoints.
* The Bridge S3 model artifact bucket.
* The Bridge Sagemaker IAM role.

## Analytics

Bridge collects *completely anonymous* usage metrics by default.

We collect the following metrics:

- Count of Bridge deploy target init/destroys. Collected when you run `bridge init/destroy XXX`.
- Count of Bridge model versions deployed by Bridge. Collected when you run `bridge run`.

Here is a sample of the data collected for a single
iteration of the `bridge run` control loop:

```
{
    'deploy_kind': 'sagemaker',
    'num_deployments': 3,
    'num_deployments_created': 0,
    'num_deployments_deleted': 0,
    'execution_time': 0.7254068851470947
}
```

To opt out, set the environment variable `BRIDGE_ANALYTICS_OPT_OUT=1`. You can do this by adding
`-e BRIDGE_ANALYTICS_OPT_OUT=1` when you run Bridge in docker. For example:

```
docker run -it \
    -e BRIDGE_MLFLOW_REGISTRY_URI=${MLFLOW_REGISTRY_URI} \
    -e BRIDGE_MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI} \
    -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
    -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
    -e AWS_DEFAULT_REGION=${AWS_REGION} \
    -e BRIDGE_ANALYTICS_OPT_OUT=1 \
    quay.io/domino/bridge:latest
```

## Development

#### 1. In this directory (`domino-research/bridge`): 

```bash
# Install as local package
pip install -e .
```

#### 2. Next, configure any environment variables, most importantly AWS credentials
   and MlFlow tracking and registry URIs:

* `BRDG_DEPLOY_AWS_PROFILE`: AWS profile for Sagemaker deployer (if different from MlFlow backend).
* `BRDG_DEPLOY_AWS_INSTANCE_TYPE`: AWS instance type for Sagemaker endpoints (default ml.t2.medium).
* `LOG_LEVEL`: Customize log level (default INFO).
* `BRIDGE_MODEL_CACHE_PATH`: Path for caching model artifacts (default .brdg-models)
* `BRIDGE_SCAN_INTERVAL_S`: Control loop refresh interval (default 15s).
* `BRIDGE_MLFLOW_REGISTRY_URI`: MlFlow registry uri.
* `BRIDGE_MLFLOW_TRACKING_URI`: MlFlow tracking uri.

In addition, you can use any standard `boto3` or MlFlow environment variables.

#### 3. Finally, run the control loop:

```bash
bridge init sagemaker
bridge run
```

Any changes you make to the code will be picked up only on a restart of `bridge run`.

## Linting / Testing

To run our linting/testing:

```
pip install -r requirements-dev.txt

# Type check
mypy bridge

# Lint
flake8 bridge

# Unit tests (only run when AWS credentials present and take 20+ minutes)
# WARNING: the tests will teardown all brdg resources in the target account
# and region, so only use in an account/region without production models.
python -m pytest

# Automatically fix lints
black .
```

We also have these set up as pre-commit hooks. To use pre-commit:

```
pip install -r requirements-dev.txt

# install pre-commit
pre-commit install
```

The checks above will run on each git commit.

## Build Docker Image

```
docker build .
```
