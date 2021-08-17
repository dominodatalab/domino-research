# Bridge

The easiest way to deploy from MLFlow to SageMaker 

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

[Check out a Loom recording of this Quick Start!](https://www.loom.com/share/c4498403c2794664a91be0d8e5119ecf)

This quickstart assumes that you already have an Mlflow registry to work with.
If do not have a registry, or would like to create a new registry for testing,
please follow our [guide to setting up Mlflow for local testing](#mlflow-quickstart).

First, run the `bridge init` to create the AWS resources that Bridge needs to operate.
Runing this command will create:

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

That's it! Bridge will begin syncing model versions from MlFlow to
Sagemaker! By default, it will sync versions assigned to Production and
Staging as well as the most recent version auto-tagged as `Latest`.

To stop syncing, simply exit the container process. If you want
to resume, re-run the same command.

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

## Development

1. In this directory (`domino-research/bridge`): 

```bash
# Install as local package
pip install -e .
```

2. Next, configure any environment variables, most importantly AWS credentials
   and MlFlow tracking and registry URIs:

* `BRDG_DEPLOY_AWS_PROFILE`: AWS profile for Sagemaker deployer (if different from MlFlow backend).
* `BRDG_DEPLOY_AWS_INSTANCE_TYPE`: AWS instance type for Sagemaker endpoints (default ml.t2.medium).
* `LOG_LEVEL`: Customize log level (default INFO).
* `BRIDGE_MODEL_CACHE_PATH`: Path for caching model artifacts (default .brdg-models)
* `BRIDGE_SCAN_INTERVAL_S`: Control loop refresh interval (default 15s).
* `BRIDGE_MLFLOW_REGISTRY_URI`: MlFlow registry uri.
* `BRIDGE_MLFLOW_TRACKING_URI`: MlFlow tracking uri.

In addition, you can use any standard `boto3` or MlFlow environment variables.

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
flake8 bridge

# Unit tests (only run when AWS credentials present and take 20+ minutes)
python -m pytest

# Automatically fix lints
black .
```

## Build Docker Image

```
docker build .
```

## Mlflow Quickstart

This is a quick guide to running Mlflow locally for testing. A full Mlflow
installation consists of 3 components:

* Mlflow tracking server / model registry
* Database backend -  stores run and model metadata
* Storage backend - stores run and model artifacts

While it is possible to run just the Mlflow server, the database backend is
required to use the model registry. Furthermore, for Bridge to be able to fetch
artifacts, you must use a non-local storage backend. We believe the simplest
option is to configure an S3 bucket for this artifact storage.

This guide assumes that you have:

* Docker installed on your machine.
* `docker-compose` installed on your machine.
* AWS credentials for creating and accessing S3 buckets. 

**This is not a production deployment.**

### Steps 

1. Set environment variables:

```
export AWS_REGION=
export AWS_BUCKET_NAME=
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
```

2. Create S3 bucket:

```
aws s3api create-bucket --bucket $AWS_BUCKET_NAME --acl private --create-bucket-configuration "{\"LocationConstraint\":\"${AWS_REGION}\"}"
```

3. Change to the `bridge/examples/mlflow` directory and run `docker-compose up -d`.

It should take about 30 seconds to start up and that's it! You should be able
to navigate to `http://localhost:5000` to see the Mlflow UI. When configuring
Bridge and any Python Mlflow clients, you should use `http://localhost:5000`
for your tracking and registry URLs. 
