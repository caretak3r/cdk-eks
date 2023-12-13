import os

# CFN Parameters
STACK_STAGE = os.environ.get("STACK_STAGE", "alpha")
STACK_PREFIX = os.environ.get("STACK_PREFIX", "tkp")
STACK_AFFIX = os.environ.get("STACK_AFFIX", "rev7")
DEPLOY_VPC_STACK = os.environ.get("DEPLOY_VPC_STACK", "true")
AUTHORIZED_ROLE_LIST = [
    "arn:aws:iam::111111111111:role/token-prowlers-eks-role",
]
DEFAULT_DATABASE_NAME = os.environ.get("DEFAULT_DATABASE_NAME", "")
DEFAULT_DATABASE_USERNAME = os.environ.get("DEFAULT_DATABASE_USERNAME", "")
