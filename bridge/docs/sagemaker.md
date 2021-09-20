# AWS Sagemaker Deploy Target Docs

## Permissions

The sections below describe the AWS permissions needed by the Bridge commands
for the Sagemaker Deploy Target.

### 1. Initialization

Running the `init` command will create:

* An S3 bucket for model artifacts.
* An IAM role for Sagemaker execution, `bridge-sagemaker-execution`,
  that will allow SageMaker to assume the SagemakerFullAccess managed policy.

This means the AWS IAM user specified by the `AWS_ACCESS_KEY_ID` and
`AWS_SECRET_ACCESS_KEY` will need access to the following permissions:
- `s3:CreateBucket`
- `iam:CreateRole`
- `iam:AttachRolePolicy`

To create an IAM user with these permissions, see section 3 below.

### 2. Running

Running the `run` command will using Bridge to create, update, and delete  SageMaker models, endpoints, and endpoint configurations in your AWS account as you make changes in your
registry.

This means the AWS IAM user specified by the `AWS_ACCESS_KEY_ID` and
`AWS_SECRET_ACCESS_KEY` will need access to the following permissions:

- List/describe/create/delete SageMaker Endpoints, EndpointConfigs, and Models
- List, put, and delete objects in the `AWS_BUCKET_NAME` configured in your shell
- Have the `IAM::PassRole` permission needed to pass the `bridge-sagemaker-execution` role created during init to SageMaker endpoints.

To create an IAM user with these permissions, see section 3 below.

### 3. Destroy

Running the `destroy` command will remove:

* All Bridge-created Sagemaker models and endpoints.
* The Bridge S3 model artifact bucket.
* The Bridge Sagemaker IAM role.

This means the AWS IAM user specified by the `AWS_ACCESS_KEY_ID` and
`AWS_SECRET_ACCESS_KEY` will need access to the following permissions:
- `s3:DeleteBucket`
- `iam:DeleteRole`
- `iam:DetachRolePolicy`

To create an IAM user with these permissions, see section 3 below.

## Passing Permissions to Bridge in Docker

Internally, Bridge uses the standard AWS CLI and boto3 SDK. This means
that you can configure access to AWS in the same ways you would locally.

We suggest setting the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
environment variables in addition to the other environment variables
specified in the docs. However, you can also
use [named profiles](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html) by mounting your AWS profile config file to the docker container and setting the `AWS_PROFILE` environment variable.

## Creating Restricted, Bridge-specific AWS IAM Users

It is best practice to use AWS IAM users with the minimal permissions needed for their task. To create such a user for Bridge `init`/`destroy` and `run` commands respectively, do the following:

### Init/Destroy IAM User

1. Sign into the AWS Management Console
2. Access the IAM Service
3. Navigate to Policies in the left menu
4. Click the button to create a Policy
5. Switch to the JSON editor, clear the existing content, and paste the content below. DO NOT proceed to the next step.
6. Find your account ID and paste it to replace the 4 instances of `<YOUR_ACCOUNT_ID>`:
    1. In a terminal configured with existing AWS access, run `aws sts get-caller-identity`
       and copy the account id.
    2. In the management console, select your username in the top right of the navigation bar
       and copy the number next to "my account".
7. Replace the 1 instances of `<YOUR_AWS_BUCKET_NAME>` with the value you'll use for your `AWS_BUCKET_NAME` environment variable.
8. When you've made the replacements above, proceed to the next step and give your new policy a descriptive name like `BridgeInitDestroy`
9. Navigate to users in the IAM left menu
10. Click the button to add users, input a username `BridgeInitDestroyUser` and select programmatic access
11. Under set permissions, select "attach an existing policy" and then find and select the policy you just created
12. Copy the Access Key and Secret Access Key and use them in the init/destroy steps in the [quickstart guide](../README.md)

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "ManageRole",
            "Effect": "Allow",
            "Action": [
                "iam:CreateRole",
                "iam:DeleteRole",
                "iam:DetachRolePolicy",
                "iam:AttachRolePolicy"
            ],
            "Resource": "arn:aws:iam::<YOUR_ACCOUNT_ID>:role/bridge-sagemaker-execution"
        },
        {
            "Sid": "ManageBucket",
            "Effect": "Allow",
            "Action": [
                "s3:CreateBucket",
                "s3:DeleteBucket"
            ],
            "Resource": ["arn:aws:s3:::<YOUR_AWS_BUCKET_NAME>"]
        },
        {
            "Sid": "DeleteSagemakerResources",
            "Effect": "Allow",
            "Action": [
                "sagemaker:DeleteEndpointConfig",
                "sagemaker:DeleteModel",
                "sagemaker:DeleteEndpoint",
            ],
            "Resource": [
                "arn:aws:sagemaker:*:<YOUR_ACCOUNT_ID>:endpoint-config/brdg-*",
                "arn:aws:sagemaker:*:<YOUR_ACCOUNT_ID>:model/brdg-*",
                "arn:aws:sagemaker:*:<YOUR_ACCOUNT_ID>:endpoint/brdg-*"
            ]
        },
    ]
}
```

### Run IAM User

1. Sign into the AWS Management Console
2. Access the IAM Service
3. Navigate to Policies in the left menu
4. Click the button to create a Policy
5. Switch to the JSON editor, clear the existing content, and paste the content below. DO NOT proceed to the next step.
6. Find your account ID and paste it to replace the 4 instances of `<YOUR_ACCOUNT_ID>`:
    1. In a terminal configured with existing AWS access, run `aws sts get-caller-identity`
       and copy the account id.
    2. In the management console, select your username in the top right of the navigation bar
       and copy the number next to "my account".
7. Replace the 2 instances of `<YOUR_AWS_BUCKET_NAME>` with the value you'll use for your `AWS_BUCKET_NAME` environment variable.
8. When you've made the replacements above, proceed to the next step and give your new policy a descriptive name like `BridgeRun`
9. Navigate to users in the IAM left menu
10. Click the button to add users, input a username like `BridgeRunUser` and select programmatic access
11. Under set permissions, select "attach an existing policy" and then find and select the policy you just created
12. Copy the Access Key and Secret Access Key and use them in the steps in the [quickstart guide](../README.md)

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "ListObjectsInBucket",
            "Effect": "Allow",
            "Action": ["s3:ListBucket"],
            "Resource": ["arn:aws:s3:::<YOUR_AWS_BUCKET_NAME>"]
        },
        {
            "Sid": "AllObjectActions",
            "Effect": "Allow",
            "Action": "s3:*Object*",
            "Resource": ["arn:aws:s3:::<YOUR_AWS_BUCKET_NAME>/*"]
        },
        {
            "Sid": "ManageSagemakerResources",
            "Effect": "Allow",
            "Action": [
                "sagemaker:CreateModel",
                "sagemaker:DeleteEndpointConfig",
                "sagemaker:CreateEndpoint",
                "sagemaker:DescribeModel",
                "sagemaker:DeleteModel",
                "sagemaker:UpdateEndpoint",
                "sagemaker:CreateEndpointConfig",
                "sagemaker:DescribeEndpointConfig",
                "sagemaker:DeleteEndpoint",
                "sagemaker:InvokeEndpointAsync",
                "sagemaker:DescribeEndpoint",
                "sagemaker:InvokeEndpoint"
            ],
            "Resource": [
                "arn:aws:sagemaker:*:<YOUR_ACCOUNT_ID>:endpoint-config/brdg-*",
                "arn:aws:sagemaker:*:<YOUR_ACCOUNT_ID>:model/brdg-*",
                "arn:aws:sagemaker:*:<YOUR_ACCOUNT_ID>:endpoint/brdg-*"
            ]
        },
        {
            "Sid": "ListSagemakerResources",
            "Effect": "Allow",
            "Action": [
                "sagemaker:ListEndpointConfigs",
                "sagemaker:ListModels",
                "sagemaker:ListEndpoints"
            ],
            "Resource": "*"
        },
        {
            "Sid": "PassRole",
            "Effect": "Allow",
            "Action": "iam:PassRole",
            "Resource": "arn:aws:iam::<YOUR_ACCOUNT_ID>:role/bridge-sagemaker-execution"
        },
    ]
}
```