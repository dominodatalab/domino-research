## MLflow Quickstart

This is a quick guide to running and MLflow locally. A full MLflow
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

### 1. Configure your shell environment

**If you do not plan to use Bridge, you can skip this step.**

If you are going to use your new MLflow registry with
[Bridge](https://github.com/dominodatalab/domino-research/tree/main/bridge),
you need to configure your shell for AWS access before proceeding.
Detailed instructions are in the
[Bridge README](https://github.com/dominodatalab/domino-research/tree/main/bridge).

### 2. Start MLflow

Make sure you're in the `guides/mlflow` subdirectory then
run the command below to start MLflow:

```
docker-compose up
```

MLflow will take about 15-30 seconds to start up and that's it!
You should be able to navigate to `http://localhost:5000` to see
the MLflow UI.

### 3. Add model versions to the MLflow registry

Use the steps below to quickly populate your new local registry
with a couple model versions so that you can try out the tools in this repo.

1. Open a new terminal tab/window
2. Change to/stay in the `guides/mlflow` directory
3. Run `source .env` to configure your shell's environment variables
4. Run `pip install -r scikit_elasticnet_wine/requirements.txt` to install the required packages. We strongly suggest doing this in a virtual environment with Python 3.7+ as the base python such that `pip == pip3`. If not, you will need to ensure you are installing into a valid Python3 runtime and adjust the commands below to use this runtime.
5. Run `python scikit_elasticnet_wine/train.py 0.1` to train the model
6. Run `python scikit_elasticnet_wine/train.py 0.5` to train the model
   again with a different value of the `alpha` hyperparameter.
7. Head to `localhost:5000` to view the results.

The `train.py` script trains a simple Elasticnet model on wine quality data,
tracks the training as an MLflow run (under 'Experiments' in the MLflow UI),
and registers  the run as a new version of the `ScikitElasticnetWineModel`
in the MLflow Model Registry (under 'Models' in the MLflow UI).

### 4. Using the MLflow registry in your own scripts

If you'd like to use your local MLflow registry in your own code,
you can use the sample code below:

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