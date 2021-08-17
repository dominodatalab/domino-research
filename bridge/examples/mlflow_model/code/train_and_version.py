import numpy as np
from sklearn.linear_model import LinearRegression
import mlflow


# configure Mlflow client
REMOTE_SERVER_URI = "http://localhost:5000"
MODEL_NAME = "SimpleLinearRegression"

mlflow.set_tracking_uri(REMOTE_SERVER_URI)

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
    tracking_uri=REMOTE_SERVER_URI, registry_uri=REMOTE_SERVER_URI
)

try:
    client.create_registered_model(MODEL_NAME)
except mlflow.exceptions.MlflowException:
    # model already exists
    pass

client.create_model_version(MODEL_NAME, run.info.artifact_uri, run.info.run_id)
