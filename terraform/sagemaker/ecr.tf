data "aws_sagemaker_prebuilt_ecr_image" "scikit" {
  repository_name = "sagemaker-scikit-learn"
  image_tag       = "0.23-1-cpu-py3"
}
