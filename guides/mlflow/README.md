## MLflow Quickstart

This is a quick guide to running and MLflow locally. A full MLflow
installation consists of 3 components:

* MLflow tracking server / model registry
* Database backend -  stores run and model metadata
* Storage backend - stores run and model artifacts

While it is possible to run just the MLflow server, the database backend is
required to use the model registry. Furthermore, to be able to fetch
artifacts, you must use a non-local-file-based storage backend.

This guide uses `docker-compose` to run Mlflow, Postgres (as the database backend),
and Minio as an S3-compatible artifact backend.

This guide assumes that you have:

* Docker installed on your machine.
* `docker-compose` installed on your machine.

**This is not a production-grade deployment of Mlflow.**

### 0. Clone this repo

Clone the repo and change to the `guides/mlflow` directory.

### 1. Start Mlflow

Make sure you're in the `guides/mlflow` subdirectory.
Run the command below to start mlflow.

```
docker-compose up
```

MLflow will take about 30-60 seconds to start up and that's it!
You should be able to navigate to `http://localhost:5000` to see
the MLflow UI.

### 2. Add model versions to the local MLFlow Registry.

We have an example model training script that demonstrates
how to use an Mlflow registry. It's a quick way to populate
your local registry with a few model versions to try out
the tools in this repo.

If you have your own model code and don't want to use our
example model, skip ahead to section 3 below.

Follow these steps to train a model and register it in MLflow:

1. Open a new terminal tab/window
2. Change to/stay in the `guides/mlflow` directory
3. Run `source .env` to configure your shell's environment variables
4. Run `pip install -r scikit_elasticnet_wine/requirements.txt` to install
   the required packages.
5. Run `python scikit_elasticnet_wine/train.py 0.1` to train the model
6. Run `python scikit_elasticnet_wine/train.py 0.5` to train the model
   again with a different value of the `alpha` hyperparameter.
7. Head to `localhost:5000` to view the results.

The `train.py` script trains a simple Elasticnet model on wine quality data,
tracks the training as an MLflow run (under 'Experiments' in the MLflow UI),
and registers  the run as a new version of the `ScikitElasticnetWineModel`
in the MLflow Model Registry (under 'Models' in the MLflow UI).

### 3. Using the MLflow registry in your own scripts

If you'd like to use your local MLflow registry in your own code,
you'll need the following config:

```python
import os
import mlflow

SERVER_URI = "http://localhost:5000"
S3_ENDPOINT_URL = "http://localhost:9000"

os.environ["MLFLOW_S3_ENDPOINT_URL"] = S3_ENDPOINT_URL

# For MLflow tracking:
mlflow.set_tracking_uri(SERVER_URI)
# ...

# For the MLflow API client:
MlflowClient(
    registry_uri=SERVER_URI, tracking_uri=SERVER_URI
)
# ...
```