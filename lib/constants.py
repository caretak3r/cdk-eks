import os

# CFN Parameters
STACK_STAGE = os.environ.get("STACK_STAGE", "beta")
STACK_PREFIX = os.environ.get("STACK_PREFIX", "tkp")
STACK_AFFIX = os.environ.get("STACK_AFFIX", "rev6")
AUTHORIZED_ROLE_LIST = [
    "arn:aws:iam::728168703404:role/token-prowlers-eks-role",
]
DEFAULT_DATABASE_NAME = os.environ.get("DEFAULT_DATABASE_NAME", "")
DEFAULT_DATABASE_USERNAME = os.environ.get("DEFAULT_DATABASE_USERNAME", "")
