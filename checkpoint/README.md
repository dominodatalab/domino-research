# :passport_control: Checkpoint

Model approval layer for your model registry.

![build](https://github.com/dominodatalab/domino-research/actions/workflows/checkpoint.yml/badge.svg?branch=main)
[![Docker Repository on Quay](https://quay.io/repository/checkpoint/bridge/status "Docker Repository on Quay")](https://quay.io/repository/domino/checkpoint)

## Why

## Quick Start

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
