import os

# CFN Parameters
STACK_STAGE = os.environ.get("STACK_STAGE", "alpha")
STACK_PREFIX = os.environ.get("STACK_PREFIX", "tkp")
STACK_SUFFIX = os.environ.get("STACK_SUFFIX", "rev11")
STACK_MANAGED_BY = "aws-cdk"
DEPLOY_VPC_STACK = os.environ.get("DEPLOY_VPC_STACK", "true")
AUTHORIZED_ROLE_LIST = ["arn:aws:iam::111111111111:role/token-prowlers-eks-role"]
APP_DATABASE_NAME = os.environ.get("APP_DATABASE_NAME", "")
APP_DATABASE_USERNAME = os.environ.get("APP_DATABASE_USERNAME", "")
