import numpy as np
from sklearn.linear_model import LinearRegression
import mlflow


REMOTE_SERVER_URI = "http://localhost:5000"
MODEL_NAME = "SimpleLinearRegression"

# configure Mlflow client
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

# Create new model version for model MODEL_NAME
# In the call below '/model' refers to the folder in the
# run's artifacts that contains the MLmodel file.
mlflow.register_model(f"runs:/{run.info.run_id}/model", MODEL_NAME)
