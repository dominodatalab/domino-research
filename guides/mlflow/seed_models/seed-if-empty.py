from mlflow.tracking import MlflowClient
import subprocess

client = MlflowClient(
            registry_uri="http://mlflow:5555",
            tracking_uri="http://mlflow:5555"
)

models = client.list_registered_models()

if len(models) == 0:
    list_files = subprocess.run(["python", "/home/scikit_elasticnet_wine/train.py", "0.1"])
    list_files = subprocess.run(["python", "/home/scikit_elasticnet_wine/train.py", "0.5"])
    list_files = subprocess.run(["python", "/home/scikit_elasticnet_wine/train.py", "0.9"])

    client.transition_model_version_stage(
        name="ScikitElasticnetWineModel",
        version=1,
        stage="Production"
    )

    client.transition_model_version_stage(
        name="ScikitElasticnetWineModel",
        version=2,
        stage="Staging"
    )
