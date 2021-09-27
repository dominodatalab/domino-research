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

<a name="try-bridge-in-our-hosted-sandbox"></a>

### Option 1: Try Bridge in our Hosted Sandbox

We're hosting a sandbox version of MLflow with Bridge at [mlflow.research.dominodatalab.com](https://bit.ly/2W7wy2h). Try the following in the sandbox:

#### Query the model version running in production

Run the command below to query the model version currently in Production. In the step below, you'll update the version in Production and compare the new inference result it generates to the result you get from this command:

```bash
curl http://bridge.research.dominodatalab.com/ScikitElasticnetWineModel/Production/invocations -H 'Content-Type: application/json' -d '{"data":[[0.1, 0.1, 0.5, 0.66, 2, 0.6, 0.17, 8, 1.1, 1.23, 11]]}'
```

#### Promote a new model version to production

1. Click into the `ScikitElasticNetWineModel` in the [MLflow models tab](https://bit.ly/2W7wy2h).
2. Click into a version that is not marked as `Production`.
3. Use the stage control in the top right to move the version into `Production`.
   (When prompted, select the option to archive the current Production version).
4. Bridge will detect the change in 15-20 seconds and will update the production endpoint with the new model version.

#### Query the model again

Rerun the command below and observe the new result. Bridge detected the new version tagged as `Production` and updated the `Production` endpoint.

```bash
curl http://bridge.research.dominodatalab.com/ScikitElasticnetWineModel/Production/invocations -H 'Content-Type: application/json' -d '{"data":[[0.1, 0.1, 0.5, 0.66, 2, 0.6, 0.17, 8, 1.1, 1.23, 11]]}'
```

### Option 2: Run yourself (locally or on a self-hosted server)

When you complete the steps below, Bridge will monitor your MLflow registry and, upon seeing a new version of a model or an update to a version's stage, will create/update inference endpoints. You'll have always-up-to-date endpoints for the `Latest`, `Staging` and `Production` versions of each of the models in your MLflow registry.

#### 0. MLflow

Bridge deploys and updates hosted models based on changes in your MLflow registry. This means you'll need an MLflow registry to use Bridge.

***If you don't have an MLflow registry***, or want a new registry just for testing Bridge, follow our 5-min [local MLflow quickstart](https://bit.ly/3AvThUN). *Note: The local MLflow registry you'll set up only supports the Localhost Deploy Target*

***If you want to use an existing MLflow registry***, set the environment variables below with the correct values - usually just the hostname of your registry like `http://mlflow.acme.org`. Do this by running this command in your terminal - editing the template values:

```bash
# Only needed if you are using an existing MLflow registry
export BRIDGE_MLFLOW_URI=http://mlflow.acme.org
```

<details>
  <summary>Note: Bridge deploys MLflow Model Versions with a valid MLmodel file. Expand for details.</summary>
  
  </br>

  Bridge deploys *model versions* in MLflow Model Registry (not runs in the Experiment Manager). Models must use the MLflow [Model Storage Format](https://www.mlflow.org/docs/latest/models.html#storage-format). I.E, the model must have a valid [MLmodel](https://www.mlflow.org/docs/latest/models.html) file in the artifacts associated with each of its versions. This is usually achieved by calling `mlflow.<framework>.log_model` or using the `mlflow.create_model_version` command with appropriate inputs.
</details>


#### 1. Select a Deploy Target

Bridge supports multiple *deploy targets* (services that Bridge can deploy your models to so that they can be used for inference). If you're new to Bridge, we suggest you start with the *localhost deploy target*:

- [Localhost Deploy Target](#local-target) - models are run in the Bridge container and are accessible on localhost (run Bridge on a server with open ports to expose models for public consumption).

- [SageMaker Deploy Target](#sagemaker-target) - models are deployed to SageMaker Endpoints and are accessible based on your AWS config.

- [{Your Preferred Target Here}](https://domino-research.slack.com/archives/C02FJ1RH5AL) - If you're interested in other deployment targets, let us know through the community [Slack](https://domino-research.slack.com/archives/C02FJ1RH5AL).

#### Local Deploy Target
<a name="local-target"></a>

#### 1. Run Bridge

*Using the local MLflow from our MLflow guide:*

On macOS:
```
docker run -it \
    -p 3000:3000 \
    -e BRIDGE_DEPLOY_KIND=localhost \
    -e BRIDGE_MLFLOW_URI=http://host.docker.internal:5555 \
    -e MLFLOW_S3_ENDPOINT_URL=http://host.docker.internal:9000 \
    -e MLFLOW_S3_IGNORE_TLS=true \
    -e AWS_ACCESS_KEY_ID=AKIAIfoobar \
    -e AWS_SECRET_ACCESS_KEY=deadbeef \
    -e AWS_DEFAULT_REGION=us-east-2 \
    quay.io/domino/bridge:latest
```

On Linux:
```
docker run -it \
    -p 3000:3000 \
    -e BRIDGE_DEPLOY_KIND=localhost \
    -e BRIDGE_MLFLOW_URI=http://localhost:5555 \
    -e MLFLOW_S3_ENDPOINT_URL=http://localhost:9000 \
    -e MLFLOW_S3_IGNORE_TLS=true \
    -e AWS_ACCESS_KEY_ID=AKIAIfoobar \
    -e AWS_SECRET_ACCESS_KEY=deadbeef \
    -e AWS_DEFAULT_REGION=us-east-2 \
    quay.io/domino/bridge:latest
```

*Using your own MLflow:*

```
docker run -it \
    -p 3000:3000 \
    -e BRIDGE_DEPLOY_KIND=localhost \
    -e BRIDGE_MLFLOW_URI=${BRIDGE_MLFLOW_URI} \
    -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
    -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
    -e AWS_DEFAULT_REGION=${AWS_REGION} \
    quay.io/domino/bridge:latest
```

#### 2. Query your Deployed Models

That's it! Bridge will begin syncing model versions from MLflow and running them on Localhost. When you push a new version, Bridge will update the `latest` endpoint. If you tag a new version for `Staging` or `Production`, Bridge will update the respective endpoint. Welcome to RegistryOps :tada:.

To query your models, send a POST request to `localhost:3000/<ModelName>/<Stage>/invocations` with a JSON and headers body matching the [MLflow model deployment docs](https://www.mlflow.org/docs/latest/models.html#deploy-mlflow-models).
- The Stage is one of `Latest`, `Staging` and `Production`. If you get a 404 error, make sure you have a version in the model that is in the stage you are querying.
- Port `3000` is the port set in the `run` command above. If you use a different host port in the `run` command - for example, `-p 6789:3000` - you should query `localhost:6789`.

**Note:** It may take 30 seconds or more to build the initial Conda environment for your model as specified in the `conda.yml` from the `MLmodel` file. During this time, you will not be able to query the model. The length of the build depends on your internet speed and the complexity of your environment. Identical environments are cached and re-used. So, updates to models, after first deploy, have only a few seconds of down time.

To stop syncing and teardown your models, simply exit the container process. If you want to resume, re-run the `run` command from the step above.

********************************

#### SageMaker Deploy Target
<a name="sagemaker-target"></a>

Check out a 7 min demo of Bridge deploying to SageMaker [here](https://bit.ly/39tL8nz).

#### 1. Configure AWS Access

First, we'll configure your terminal with the environment variables that Bridge will use to access AWS in order to deploy to SageMaker. To get started, you will need an `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` for a user with read/write permissions for S3, SageMaker and IAM.

To configure AWS access for Bridge, run this command in your terminal - editing the template values:

```bash
# Use credentials for an AWS user
# with read/write to S3, SageMaker and IAM
export AWS_ACCESS_KEY_ID=XXX
export AWS_SECRET_ACCESS_KEY=XXX

# You can change these or stick with the defaults supplied here.
export AWS_REGION=us-east-2
export AWS_DEFAULT_REGION=us-east-2
```

If you'd like to know which AWS permissions are needed for each command so that you can create a restricted-access IAM user for Bridge, see the AWS SageMaker Deploy Target permissions docs [here](./docs/sagemaker.md#sagemaker-commands).

#### 2. Initialize Bridge in AWS

Run the `init` command to create the AWS resources that Bridge needs to operate. This command only needs to be run once for a given AWS account and region.

To initialize Bridge, run the command below in the terminal you configured:

```
docker run -it \
    -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
    -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
    -e AWS_DEFAULT_REGION=${AWS_REGION} \
    quay.io/domino/bridge:latest init sagemaker
```

If you'd like to know exactly what the command does and what permissions it needs, see the AWS SageMaker Deploy Target docs [here](./docs/sagemaker.md#sagemaker-command-init).

#### 3. Run Bridge

To run Bridge, select the right command from the options below
and run it in the terminal you configured:

*Using your own MLflow:*

```
docker run -it \
    -e BRIDGE_MLFLOW_URI=${BRIDGE_MLFLOW_URI} \
    -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
    -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
    -e AWS_DEFAULT_REGION=${AWS_REGION} \
    quay.io/domino/bridge:latest
```

If you'd like to know exactly what the command does and what permissions it needs, see the AWS SageMaker Deploy Target docs [here](./docs/sagemaker.md#sagemaker-command-run).

*Using the local MLflow from our MLflow guide*

The local MLflow set up using our guide **does not support** deploying to SageMaker. Follow the steps under the [Local Deploy Target](#local-target) instead.

#### 4. Query your Deployed Models

That's it! Bridge will begin syncing model versions from MlFlow to
SageMaker. When you push a new version, Bridge will update the `latest`
endpoint. If you tag a new version for `Staging` or `Production`, Bridge
will update the respective endpoint. Welcome to RegistryOps :tada:.

To query your models, use the standard `InvokeEndpoint` command - documented [here](https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_runtime_InvokeEndpoint.html). The name of the endpoint will be `brdg-<ModelName>-<Stage>` where Stage is one of `Latest`, `Staging` and `Production`.

**Note:** SageMaker endpoints take 5-10 mins to launch and update. This means there will be a delay before a new brand new model stage is available to query. Updates to existing model stages are done without downtime with the old version returning results until the new version is ready.

To stop syncing, simply exit the container process. If you want
to resume, re-run the `run` command from the step above. This **will NOT** stop the endpoints in AWS. To do that, see the clean up step below.

#### 5. Cleanup

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

If you'd like to know exactly what the command does and what permissions it needs, see the AWS SageMaker Deploy Target docs [here](./docs/sagemaker.md#sagemaker-command-destroy).

************************************

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
    -e BRIDGE_MLFLOW_URI=${BRIDGE_MLFLOW_URI} \
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

* `BRDG_DEPLOY_AWS_PROFILE`: AWS profile for SageMaker deployer (if different from MlFlow backend).
* `BRDG_DEPLOY_AWS_INSTANCE_TYPE`: AWS instance type for SageMaker endpoints (default ml.t2.medium).
* `LOG_LEVEL`: Customize log level (default INFO).
* `BRIDGE_MODEL_CACHE_PATH`: Path for caching model artifacts (default .brdg-models)
* `BRIDGE_SCAN_INTERVAL_S`: Control loop refresh interval (default 15s).
* `BRIDGE_MLFLOW_URI`: MlFlow registry uri.

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
