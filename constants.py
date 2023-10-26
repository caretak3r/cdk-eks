import os

# CFN Parameters
EKS_STAGE = os.environ.get("EKS_STAGE", "beta")
STACK_PREFIX = os.environ.get("STACK_PREFIX", "tkp")
STACK_AFFIX = os.environ.get("STACK_AFFIX", "rev5")
