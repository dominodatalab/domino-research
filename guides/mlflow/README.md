## MLflow Quickstart

This is a quick guide to running and MLflow locally. A full MLflow
installation consists of 3 components:

* MLflow tracking server / model registry
* Database backend -  stores run and model metadata
* Storage backend - stores run and model artifacts

While it is possible to run just the MLflow server, the database backend is
required to use the model registry. Furthermore, to be able to fetch
artifacts, you must use a non-local storage backend. We believe the simplest
option is to configure an S3 bucket for this artifact storage. This guide
uses `docker-compose` to run Mlflow, Postgres (as the database backend), and
generates an S3 bucket for you in your account.

This guide assumes that you have:

* Docker installed on your machine.
* `docker-compose` installed on your machine.
* AWS credentials for creating and accessing S3 buckets. 

**This is not a production-grade deployment of Mlflow.**

#### 1. Set environment variables:

```
export AWS_REGION=XXX
export AWS_BUCKET_NAME=XXX
export AWS_ACCESS_KEY_ID=XXX
export AWS_SECRET_ACCESS_KEY=XXX
```

#### 2. Create S3 bucket:

```
aws s3api create-bucket --bucket $AWS_BUCKET_NAME --acl private --create-bucket-configuration "{\"LocationConstraint\":\"${AWS_REGION}\"}"
```

#### 3. Run using `docker-compose`

- Clone this repo and change to the `guides/mlflow` directory.
- In the directory, run `docker-compose up`.
- MLflow will take about 30-60 seconds to start up and that's it! You should be able
  to navigate to `http://localhost:5000` to see the MLflow UI.

#### 4. Add model versions to the local MLFlow Registry.

If you're familiar with Mlflow and have a model at hand, you
can add a model yourself. Simply configure the Mlflow Python clients
with `http://localhost:5000` as the tracking and registry URLs.
If you don't have a model handy, you can run our example script
to add a new model and model version to the local Mlflow registry:

1. Stay in the `guides/mlflow` directory
2. Run `pip install -r scikit_model/code/requirements.txt`
3. Run `python scikit_model/code/train_and_version.py`

This trains a simple linear regression model, tracks the training as
an MLflow run, and using the run to create a new version of the
`SimpleLinearRegression` in the MLflow Model Registry.
You can run the script again to add another version to the same model.