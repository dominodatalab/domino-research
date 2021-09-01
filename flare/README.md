# Monitor

Lightweight model monitoring and alerting framework.

![build](https://github.com/dominodatalab/domino-research/actions/workflows/flare.yml/badge.svg?branch=main)

## Why

## Quick Start

## Development

#### 1. In this directory (`domino-research/flare`): 

```bash
# Install as local package
pip install -e .
```

## Linting / Testing

To run our linting/testing:

```
pip install -r requirements-dev.txt

# Type check
mypy flare

# Lint
flake8 flare

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
