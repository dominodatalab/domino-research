# Monitor

Lightweight model monitoring and alerting framework.

![build](https://github.com/dominodatalab/domino-research/actions/workflows/monitor.yml/badge.svg?branch=main)

## Why

## Quick Start

## Development

#### 1. In this directory (`domino-research/monitor`): 

```bash
# Install as local package
pip install -e .
```

## Linting / Testing

To run our linting/testing:

```
pip install -r requirements-dev.txt

# Type check
mypy monitor

# Lint
flake8 monitor

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
