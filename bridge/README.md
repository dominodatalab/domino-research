# Bridge

The easiest way to deploy from MLFlow to SageMaker

## Development

In this directory: 

```
# Install as local package
pip install -e .

# Run control loop
LOG_LEVEL=DEBUG APP_REGISTRY_URI=http://localhost:5000 bridge
```

Any changes you make to the code will be picked up on restart.

## Linting / Testing

```
pip install -r requirements-dev.txt

# Type check
mypy bridge

# Lint
flake bridge

# Unit tests
python -m pytest

# Automatically fix lints
black .
```

## Build Docker Image

```
docker build .
```
