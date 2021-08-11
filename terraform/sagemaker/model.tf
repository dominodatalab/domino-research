resource "aws_sagemaker_model" "this" {
  name               = "rs-model-a-1"
  execution_role_arn = aws_iam_role.execution_role.arn

  container {
    image          = data.aws_sagemaker_prebuilt_ecr_image.scikit.registry_path
    model_data_url = var.artifact_uri
    environment = {
      SAGEMAKER_CONTAINER_LOG_LEVEL = "20"
      SAGEMAKER_PROGRAM             = "inference.py"
      SAGEMAKER_REGION              = data.aws_region.current.name
      SAGEMAKER_SUBMIT_DIRECTORY    = var.script_uri
    }
  }
}
