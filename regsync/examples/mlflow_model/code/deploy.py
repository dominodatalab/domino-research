import mlflow.sagemaker as sm

sm.deploy(
  "test-mlflow-4",
  ".",
  execution_role_arn="arn:aws:iam::667552661262:role/kevin_sagemaker_execution",
  bucket="test-mlflow-deploy",
  image_url="667552661262.dkr.ecr.us-east-2.amazonaws.com/mlflow-pyfunc:1.19.0",
  region_name='us-east-2',
  mode='create',
  archive=False,
  instance_type='ml.m4.xlarge',
  instance_count=1,
  vpc_config=None,
  flavor="python_function",
  synchronous=True
)