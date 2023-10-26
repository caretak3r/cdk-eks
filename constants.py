import os

# CFN Parameters
EKS_STAGE = os.environ.get("EKS_STAGE", "beta")
STACK_PREFIX = os.environ.get("STACK_PREFIX", "SOMEPREFIX")

# AWS Parameters
AWS_EKS_KUBERNETES_VERSION = os.environ.get("AWS_EKS_KUBERNETES_VERSION", "1.27")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
AWS_ACCOUNT_ID = os.environ.get("AWS_ACCOUNT_ID", "")
AWS_ECR_REPOSITORY_ARN = os.environ.get("AWS_ECR_REPOSITORY_ARN", "")
AWS_ECR_REPOSITORY_URL = os.environ.get("AWS_ECR_REPOSITORY_URL", "")
AWS_EXISTING_VPC = False
AWS_VPC_ID = ""
