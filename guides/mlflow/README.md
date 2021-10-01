## MLflow Quickstart

This is a quick guide to running MLflow locally. A full MLflow
installation consists of 3 components:

* MLflow tracking server / model registry
* Database backend -  stores run and model metadata
* Storage backend - stores run and model artifacts

This guide uses `docker-compose` to run MLflow, MySQL (as the database backend),
and Minio as an S3-compatible artifact backend. You'll need Docker and `docker-compose`
installed on your machine.

### 0. Clone this repo

Clone the repo and change to the `guides/mlflow` directory.

HTTPS:  `git clone https://github.com/dominodatalab/domino-research.git && cd domino-research/guides/mlflow`

SSH:  `git clone git@github.com:dominodatalab/domino-research.git && cd domino-research/guides/mlflow`

### 1. Start MLflow

Make sure you're in the `guides/mlflow` subdirectory then run the command below to start MLflow:

```bash
docker-compose up -d
```

MLflow will take about 15-30 seconds to start up and that's it!
If you navigate to `http://localhost:5555`, you should see the MLflow UI.
You can now proceed with the quick start for the project that brought your here.

Note that we pre-seed the registry with a simple demo model called `ScikitElasticnetWineModel`.
It has 3 versions, with one marked for Staging and one marked for Production. The training
code for this model is in `seed_models/scikit_elasticnet_wine/train.py`.

### 2. [Optional] Using the MLflow registry with your own models

If you'd like to add new models using your own training code,
you can use the sample configuration below. Note that any model versions
used with Bridge will need a valid `MLmodel` specification (one that allows you to call
`mlflow models serve -m your_model`). This file will be created for you if you log
with the `mlflow.<framework>.log_model` sdk.

```python
import os
import mlflow

SERVER_URI = "http://localhost:5000"
S3_ENDPOINT_URL = "http://localhost:9000"

os.environ["MLFLOW_S3_ENDPOINT_URL"] = S3_ENDPOINT_URL
os.environ["MLFLOW_S3_IGNORE_TLS"] = true
os.environ["AWS_ACCESS_KEY_ID"] = AKIAIfoobar
os.environ["AWS_SECRET_ACCESS_KEY"] = deadbeef
    
# For MLflow tracking:
mlflow.set_tracking_uri(SERVER_URI)
# ...

# For the MLflow API client:
MlflowClient(
    registry_uri=SERVER_URI, tracking_uri=SERVER_URI
)
# ...
```

### 3. [Optional] Stop MLflow

Make sure you're in the `guides/mlflow` subdirectory then
run the command below to stop MLflow:

```
docker-compose down
```

To wipe the artifact and metadata stored locally by MLflow, delete
the `mlflowArtifactData` and `mlflowDBData` subdirectories in the `guides/mlflow` folder.
