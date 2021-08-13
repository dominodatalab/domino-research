from pprint import pprint
import numpy as np
from sklearn.linear_model import LinearRegression
import mlflow
import os

# configure Mlflow client
remote_server_uri = "http://mlflow.gambit-sandbox.domino.tech"
mlflow.set_tracking_uri(remote_server_uri)

# enable autologging
mlflow.sklearn.autolog()

# prepare training data
X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
y = np.dot(X, np.array([1, 2])) + 3

# train a model
model = LinearRegression()
with mlflow.start_run() as run:
    model.fit(X, y)

# create model version
print(run.info)
client = mlflow.tracking.MlflowClient(
    tracking_uri=remote_server_uri, registry_uri=remote_server_uri
)
print(
    client.create_model_version(
        "CatPicDetector", run.info.artifact_uri, run.info.run_id
    )
)
