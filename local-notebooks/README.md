# Local Notebooks

Locally run JupyterLab, with configuration for environment and data sharing,
and real-time collaboration.

# Installation

## 0. Requirements

* `awscli` Version 2
* Docker

## 1. Build Container Image

```bash
docker build -t local-notebooks:latest .
```

## Provision AWS Resources

Select a region, bucket name (must be globally unique), and user name (must be unique in account):

```bash
# us-east-1 is recommended, s3fs has some known issues with other regions
export AWS_REGION=us-east-1
export AWS_BUCKET=<your unique bucket name>
export AWS_USER=local-notebooks
```

Create S3 bucket:

```bash
aws s3 mb ${AWS_BUCKET}
```

Create IAM credentials for bucket access:

```bash
# Create new IAM user
aws iam create-user --user-name ${AWS_USER}
# Create policy for access to S3 bucket created above
aws iam create-policy --policy-name ${AWS_USER} --policy-document "$(envsubst < config/policy.json)"
# Attach policy to user
aws iam attach-user-policy --user-name ${AWS_USER} --policy-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/${AWS_USER}
# Generate API credentials for user
mkdir .aws && aws iam create-access-key --user-name ${AWS_USER} > .aws/credentials
```

## Run Notebook

```bash
docker run --name local-notebook \
    -it -p 8888:8888 \
    -e JUPYTER_ENABLE_LAB=yes \
    -e NB_USER=domino-research \
    --user root \
    --cap-add SYS_ADMIN \
    --security-opt apparmor:unconfined \
    --device /dev/fuse \
    -e AWS_BUCKET=${AWS_BUCKET} \
    -e AWS_REGION=${AWS_REGION} \
    -v $(pwd)/.aws:/etc/aws \
    local-notebooks
```

# Usage

Once the notebook starts, JupyterLab will print out a link to access the UI as usual, use the one with hostname `127.0.0.1`. 

## Shared Data

The S3 bucket is mounted at `/mnt/home`, and set as the default path for the notebook. Any files you store here will be persisted to S3, and can be used by other users with a similar configuration. 

## Environments

## Real-Time Collaboration
