import os

# CFN Parameters
STACK_STAGE = os.environ.get("STACK_STAGE", "alpha")
STACK_PREFIX = os.environ.get("STACK_PREFIX", "tkp")
STACK_AFFIX = os.environ.get("STACK_AFFIX", "rev10")
STACK_MANAGED_BY = "aws-cdk"
DEPLOY_VPC_STACK = os.environ.get("DEPLOY_VPC_STACK", "true")
AUTHORIZED_ROLE_LIST = []
DEFAULT_DATABASE_NAME = os.environ.get("DEFAULT_DATABASE_NAME", "")
DEFAULT_DATABASE_USERNAME = os.environ.get("DEFAULT_DATABASE_USERNAME", "")
