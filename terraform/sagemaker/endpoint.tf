resource "aws_sagemaker_endpoint_configuration" "this" {
  name = "rs-model-a-Staging"

  production_variants {
    model_name             = aws_sagemaker_model.this.name
    initial_instance_count = 1
    instance_type          = "ml.t2.medium"
    variant_name           = "model-a-1"
  }
}

resource "aws_sagemaker_endpoint" "this" {
  name                 = "rs-model-a-Staging"
  endpoint_config_name = aws_sagemaker_endpoint_configuration.this.name
}
