# :passport_control: Checkpoint

A better process for promoting models to production.

![build](https://github.com/dominodatalab/domino-research/actions/workflows/checkpoint.yml/badge.svg?branch=main)
[![Docker Repository on Quay](https://quay.io/repository/domino/checkpoint/status "Docker Repository on Quay")](https://quay.io/repository/domino/checkpoint)

## Why

Checkpoint provides a 'pull request for Machine Learning' workflow that enables better governance for model registries. This process, which we are calling _Promote Requests_, lets data scientists request that a model version be promoted to a deployment stage (e.g. Staging or Production). Team members can then review this request with any changes in parameters and metrics highlighted. Once the request is approved, the model stage is updated in the model registy.

This process means you can trust that the model tagged Production is really meant for production. This, in turn, means you can (and should!) automatically update your model hosting infrastructure when a new model version is promoted - turning your registry into the declarative source-of-truth. We built :bridge_at_night: [Bridge](https://github.com/dominodatalab/domino-research/tree/main/bridge) to do exactly this.

## Quick Start

Checkpoint proxies your existing Mlflow registry and augments it with the Promote Request workflow.
You run Checkpoint by pointing it at your existing Mlflow registry. You then access your registry and 
Promote Requests via Checkpoint. 

### Setup

When you run the command below, you will be able to access the Mlflow registry
hosted at `YOUR_MLFLOW_REGISTRY_HOST` by visiting `localhost:5000`. This is great
way to take checkpoint for a test drive.

If you do not have a registry, or would like to create a new registry for testing,
please follow our 5-min [guide to setting up Mlflow](https://github.com/dominodatalab/domino-research/tree/main/guides/mlflow).

```bash
docker run -it \
-p 5000:5000 \
-v $(PWD):/tmp \
-e CHECKPOINT_REGISTRY_URL=<YOUR_MLFLOW_REGISTRY_HOST> \
quay.io/domino/checkpoint
```

### Usage

- To create a promote request, visit the models page in Mlflow and attempt to transition
a version to a new stage. You'll be redirected to a page where you can add/edit the Promote Request
title and description and that's it! You now have an open Promote Request, waiting for approval.

- To view a list of open promote requests, click the floating `Promote Requests` control
  at the top of any Mlflow screen.

### Sharing access with your Team

When you are ready to use checkpoint with your team, you have two options:

1. Host checkpoint yourself on a shared server - perhaps the same server you are using to run Mlflow.
  For example, run the same command above on an EC2 instance configured to allow your team
  access to the exposed port. _(Make sure that you maintain the same access controls!
  If checkpoint is publically accessible, then your Mlflow registry will be publically
  accessible (authentication coming soon!)_
  
2. Use our Heroku button to deploy Checkpoint in one click (...coming soon).

## Analytics

Checkpoint collects *completely anonymous* usage metrics by default.

We only collect the following metrics:

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
