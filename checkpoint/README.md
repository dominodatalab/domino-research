# :passport_control: Checkpoint

A better process for promoting models to production.

![build](https://github.com/dominodatalab/domino-research/actions/workflows/checkpoint.yml/badge.svg?branch=main)
[![Docker Repository on Quay](https://quay.io/repository/domino/checkpoint/status "Docker Repository on Quay")](https://quay.io/repository/domino/checkpoint)

## Why Checkpoint

Checkpoint provides a 'pull request for Machine Learning' in your model registries:
- Data scientists request that a model version be promoted to a deployment stage (e.g. Staging or Production).
  This creates a _Promote Request_.
- Team members can then review this request, with changes in any parameters and metrics highlighted.
- Once the request is approved, the model stage is updated in the model registry.

With checkpoint installed, promoted Model Versions are reviewed and can be trusted. This means you can
(and should) trigger automated updates to your model hosting/inference infra when versions are promoted.
We built [:bridge_at_night: Bridge](https://github.com/dominodatalab/domino-research/tree/main/bridge)
to enable exactly this - registry-based Continuous Deployment.

## Quick Start

You run Checkpoint by pointing it at your existing MLflow registry. You then access your MLflow registry
and Checkpoint's Promote Requests via Checkpoint. Checkpoint works by proxying your MLflow registry,
augmenting it with the Promote Request workflow.

### Try Checkpoint in our Hosted Sandbox

We're hosting a sandbox version of Checkpoint at [domino-research-checkpoint.herokuapp.com](https://bit.ly/2XF2xac). Try the following in the sandbox:

#### Create a Promote Request

1. Click into the `ScikitElasticNetWineModel` in the MLflow models tab.
2. Click into a version that is not marked as `Production`.
3. Use the stage control in the top right to move the version into `Production`.
   (When prompted, select the option to archive the current Production version).
4. You'll be presented with the new Promote Request screen, add a description and click create.
5. You'll be presented with the diff view. Note the highlighted changes in metric and parameter values. You can share this URL for a team member to review.

#### Review and Approve a Promote Request

1. If you're already in the Promote Request view, you're ready to go. If you need to create
   a new Promote Request, follow the steps above.
2. Note the highlighted changes in metric and parameter values.
3. Scroll to the bottom of the page and select the approve action from the action drop down.
4. Click submit. This approves the Promote Request and promotes the model version.
5. Navigate back to the registry using the control in the top right. The version you selected is now in Production.
6. To return to see the list of open Promote Requests, click the Checkpoint control at the top
   of any MLflow screen.


### Running locally

Checkpoint requires an MLflow registry. If you do not have a registry, or would like to create a new registry for testing,
please follow our 5-min
[guide to setting up MLflow](https://bit.ly/3tKeiZb).

When you run the command below, you will be able to access the MLflow registry
hosted at `YOUR_MLFLOW_REGISTRY_HOST` by visiting `localhost:6000`. This is great
way to take Checkpoint for a test drive. For more on using Checkpoint with your
team, see the sections below.

**Using your own MLflow:**

```bash
docker run -it \
-p 6000:5000 \
-v $(PWD):/tmp \
-e CHECKPOINT_REGISTRY_URL=<YOUR_MLFLOW_REGISTRY_HOST> \
quay.io/domino/checkpoint
```

**Using the local MLflow from our MLflow guide** 

On macOS:

```bash
docker run -it \
-p 6000:5000 \
-v $(PWD):/tmp \
-e CHECKPOINT_REGISTRY_URL=http://host.docker.internal:5000 \
quay.io/domino/checkpoint
```

On Linux:

```bash
docker run -it \
-p 6000:5000 \
-v $(PWD):/tmp \
-e CHECKPOINT_REGISTRY_URL=http://localhost:5000 \
quay.io/domino/checkpoint
```

### Usage

*Note: if you're using the local MLflow from our MLflow guide, make sure to follow the instructions*
*provided to add a few model versions with different parameters and metrics to the registry*.

- To create a promote request, visit the models page in MLflow. Click into a model and then into
  a version. Then attempt to transition the version to a new stage. You'll be redirected to the 
  new Promote Request page where you can add/edit the Promote Request title and description and
  that's it! You now have an open Promote Request, waiting for approval.

- To view a list of open promote requests, click the floating `Promote Requests` control
  at the top of any MLflow screen.

- To review a Promote Request, click into it from the list view, scroll to the bottom of the page
  and select approve (or close, if you do not want to approve) in the drop down control. Add an 
  optional comment and click submit.

### Using Checkpoint with your Team

When you are ready to use checkpoint with your team, you have two options:

1. Host checkpoint yourself on a shared server - perhaps the same server you are using to run MLflow.
  For example, run the same command used to run locally on an EC2 instance that is configured to allow
  your team access to the exposed port (6000). Make sure that you maintain the same access controls
  to the Checkpoint process that you apply to your MLflow registry! If checkpoint is publically accessible,
  then your MLflow registry will be publically accessible (authentication coming soon!).
  
2. Use our Heroku button to deploy Checkpoint in one click (just supply your MLflow URL):
  [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/domino-research/heroku-checkpoint/tree/main)

## Analytics

Checkpoint collects *completely anonymous* usage metrics by default.

We collect the following metrics:

- Count of Checkpoint server initialization events. Collected when you start the checkpoint server.

To opt out, set the environment variable `CHECKPOINT_ANALYTICS_OPT_OUT=1`. You can do this by adding
the `-e CHECKPOINT_ANALYTICS_OPT_OUT=1` flag when you run Checkpoint in docker.

## Development

#### 1. In this directory (`domino-research/checkpoint`):

```bash
# Install as local package
pip install -e .
```

To run the server:

```bash
FLASK_APP=checkpoint.app \
FLASK_ENV=development \
CHECKPOINT_REGISTRY_URL=http://YOUR_MFLOW_HOST \
flask run
```

## Linting / Testing

To run our linting/testing:

```
pip install -r requirements-dev.txt

# Type check
mypy checkpoint

# Lint
flake8 checkpoint

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
