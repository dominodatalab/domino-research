# :bridge_at_night: Bridge

The easiest way to deploy from MLflow to SageMaker 

![build](https://github.com/dominodatalab/domino-research/actions/workflows/bridge.yml/badge.svg?branch=main)
[![Docker Repository on Quay](https://quay.io/repository/domino/bridge/status "Docker Repository on Quay")](https://quay.io/repository/domino/bridge)

## Why Bridge

Bridge enables declarative model deployment with a model registry
as the source of truth.

- Data scientists manage the lifecycle of their models exclusively
  through the API and user interface of their Model registry.
  Stage labels (dev/staging/prod/etc) in the registry
  become a declarative specification of which models should be deployed.

- DevOps and machine learning engineering teams use Bridge to
  automate the often complex and frustrating management of SageMaker
  resources. You manage Bridge, Bridge herds the AWS cats and manages
  the repetitive wrapper code.

- Both teams can be confident that the models tagged in the
  registry are the models being served, without having to dig
  through git and CI logs or worrying about keeping things up to
  date manually.


## Quick Start

This quickstart has 4 steps. When you're done, Bridge will monitor your MLflow registry
and, upon seeing a new version of a model or an update to a version's stage, will create/update SageMaker endpoints. You'll have always-up-to-date hosted endpoints for the `Latest`, `Staging` and `Production` versions of each of the models in your MLflow registry.

Check out a 7 min demo of this Quick Start [here](https://bit.ly/39tL8nz).

### 1. Configure AWS and MLFlow Access

First, we'll configure your terminal with the environment variables that Bridge will use to access MLflow and AWS.

#### 1.1 AWS

Bridge currently deploys models to AWS SageMaker. This means you'll need an AWS account to use Bridge. (If you're interested in other deployment targets, let us know through [Slack](https://domino-research.slack.com/archives/C02FJ1RH5AL)). The simplest way to get started is to set the environment variables below, using an `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` for a user with read/write permissions for S3, SageMaker and IAM.

To configure AWS access for Bridge, run this command in your terminal - editing the template values:

```
# Use credentials for an AWS user
# with read/write to S3, Sagemaker and IAM
export AWS_ACCESS_KEY_ID=XXX
export AWS_SECRET_ACCESS_KEY=XXX

# You can change these or stick with the defaults supplied here.
export AWS_REGION=us-east-2
export AWS_DEFAULT_REGION=us-east-2
```

If you'd like to know which AWS permissions are needed for each command so that you can
create a restricted-access IAM user for Bridge, see the AWS Sagemaker Deploy Target permissions docs [here](./docs/sagemaker.md#sagemaker-commands).

#### 1.2 MLflow

Bridge deploys and updates hosted models based on changes in your MLflow registry. This
means you'll need an MLflow registry to use Bridge.

**If you don't have an MLflow registry**, or want a new registry just for testing Bridge, follow our 5-min [local MLflow quickstart](https://bit.ly/3AvThUN). When you have followed our guide, you can skip to step 2 - initializing bridge.

**If you want to use an existing MLflow registry**, set the environment variables below with the correct values - usually just the hostname of your registry like `http://mlflow.acme.org`.Do this by running this command in your terminal - editing the template values:

  ```
  # Only needed if you are using an existing MLflow registry
  export MLFLOW_REGISTRY_URI=http://mlflow.acme.org
  export MLFLOW_TRACKING_URI=http://mlflow.acme.org
  ```

### 2. Initialize Bridge

Run the `init` command to create the AWS resources that Bridge needs to operate. This command only needs to be run once for a given AWS account and region.

To initialize Bridge, run the command below in the terminal you configured:

```
docker run -it \
    -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
    -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
    -e AWS_DEFAULT_REGION=${AWS_REGION} \
    quay.io/domino/bridge:latest init sagemaker
```

If you'd like to know exactly what the command does and what permissions it needs, see
the AWS Sagemaker Deploy Target docs [here](./docs/sagemaker.md#sagemaker-command-init).

### 3. Run Bridge

To run Bridge, select the right command from the options below
and run it in the terminal you configured:

**Using the local MLflow from our MLflow guide** 

On macOS:
```
docker run -it \
    -e BRIDGE_MLFLOW_REGISTRY_URI=http://host.docker.internal:5000 \
    -e BRIDGE_MLFLOW_TRACKING_URI=http://host.docker.internal:5000 \
    -e MLFLOW_S3_ENDPOINT_URL=http://host.docker.internal:9000 \
    -e MLFLOW_S3_IGNORE_TLS=true \
    -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
    -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
    -e AWS_DEFAULT_REGION=${AWS_REGION} \
    quay.io/domino/bridge:latest
```

On Linux:
```
docker run -it \
    -e BRIDGE_MLFLOW_REGISTRY_URI=http://localhost:5000 \
    -e BRIDGE_MLFLOW_TRACKING_URI=http://localhost:5000 \
    -e MLFLOW_S3_ENDPOINT_URL=http://localhost:9000 \
    -e MLFLOW_S3_IGNORE_TLS=true \
    -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
    -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
    -e AWS_DEFAULT_REGION=${AWS_REGION} \
    quay.io/domino/bridge:latest
```

**Using your own MLflow:**

```
docker run -it \
    -e BRIDGE_MLFLOW_REGISTRY_URI=${MLFLOW_REGISTRY_URI} \
    -e BRIDGE_MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI} \
    -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
    -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
    -e AWS_DEFAULT_REGION=${AWS_REGION} \
    quay.io/domino/bridge:latest
```

If you'd like to know exactly what the command does and what permissions it needs, see the AWS Sagemaker Deploy Target docs [here](./docs/sagemaker.md#sagemaker-command-run).

### 4. Welcome to RegistryOps

That's it! Bridge will begin syncing model versions from MlFlow to
Sagemaker! By default, it will sync versions assigned to Production and
Staging as well as the most recent version auto-tagged as `Latest`.

If you push a new version to a model in your registry, you will see
the `Latest` endpoint for that model create/update in SageMaker with that
version. If you then tag that version as `Staging` it will create/update the
`Staging` endpoint for the model with the version. Welcome to RegistryOps.

To stop syncing, simply exit the container process. If you want
to resume, re-run the `run` command from Section 2 above.

**Note:** Bridge deploys the *models* in MLflow (not runs).
Models must use the MLflow [storage format](https://www.mlflow.org/docs/latest/models.html#storage-format).
I.E., the model must have a valid [MLmodel](https://www.mlflow.org/docs/latest/models.html)
file in the artifacts stored in each of its versions. This is
usually achieved by calling `mlflow.<framework>.log_model`
or using the `create_model_version` command with appropriate inputs.

## Cleanup

If you are done using Bridge in a given AWS account and region, you can run
the command below to remove all traces of Bridge. This will **delete all
the resources** managed by Bridge but no resources from your MLflow registry.

```
docker run -it \
    -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
    -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
    -e AWS_DEFAULT_REGION=${AWS_REGION} quay.io/domino/bridge:latest \
    destroy sagemaker
```

If you'd like to know exactly what the command does and what permissions it needs, see
the AWS Sagemaker Deploy Target docs [here](./docs/sagemaker.md#sagemaker-command-destroy).

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
