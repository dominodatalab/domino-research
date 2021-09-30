#!/bin/bash

set -ex

pip install -e .

export BRIDGE_DEPLOY_KIND=localhost
export FLASK_ENV=development
export FLASK_APP=bridge.app:main
export BRIDGE_MLFLOW_URI=http://localhost:5555
export MLFLOW_S3_ENDPOINT_URL=http://localhost:9000
export MLFLOW_S3_IGNORE_TLS=true
export AWS_ACCESS_KEY_ID=AKIAIfoobar
export AWS_SECRET_ACCESS_KEY=deadbeef
export AWS_DEFAULT_REGION=us-east-2
export BRIDGE_ANALYTICS_OPT_OUT=1
bridge run
