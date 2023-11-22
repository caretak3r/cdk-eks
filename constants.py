import os

# CFN Parameters
EKS_STAGE = os.environ.get("EKS_STAGE", "beta")
STACK_PREFIX = os.environ.get("STACK_PREFIX", "tkp")
STACK_AFFIX = os.environ.get("STACK_AFFIX", "rev5")
# AUTHORIZED_ROLE_LIST = ['arn:aws:iam::728168703404:role/AWSReservedSSO_c1s-sandbox-manchester_c5e4aa2b5eb0e3e9', 'arn:aws:iam::728168703404:role/token-prowlers-eks-role']
AUTHORIZED_ROLE_LIST = ["arn:aws:iam::728168703404:role/token-prowlers-eks-role"]
