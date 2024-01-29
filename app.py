import os
from dotenv import load_dotenv, dotenv_values
from aws_cdk import App, Environment
import lib.constants as constants

from stacks.base_stack import BaseStack
from stacks.eks_stack_mini import EksStack
from stacks.alb_stack import AlbStack

# TODO: implement these stacks
# from stacks.rds_stack import RdsStack
# from stacks.efs_stack import EfsStack
# from stacks.logging_stack import LoggingStack
# from stacks.cert_manager_stack import CertManagerStack
# from stacks.network_policy_stack import NetworkPolicyStack
# from stacks.application_stack import ApplicationStack

# TODO: use tag_stacks.py to tag stacks with default tags (managed_by, env, deployment_id)

# loads environment variables from .env file
load_dotenv(verbose=True, dotenv_path=".env", override=True)

config = dotenv_values(".env")
for key, value in config.items():
    print(f"{key}: {value}")

# initialize app
app = App()

# get environment variables from the user input (.env file)
# If you don't specify 'env', this stack will be environment-agnostic.
# Account/Region-dependent features and context lookups will not work,
# but a single synthesized template can be deployed anywhere.
env = {
    "env": Environment(
        account=os.getenv("AWS_ACCOUNT_ID"), region=os.getenv("AWS_REGION")
    )
}

# -------------------
# Create Base Stack -
# -------------------
# This will provision an S3 bucket, and set up values for vpc and subnet_ids.
# This will also create a VPC+Subnets (networking) if DEPLOY_VPC_STACK is true and no env
# values for VPC or subnets are provided.
base_stack = BaseStack(
    app,
    "BaseStack",
    stack_name=f"{constants.STACK_PREFIX}-base-stack-{constants.STACK_SUFFIX}",
    vpc_id=os.getenv("AWS_VPC_ID"),
    subnet_ids=os.getenv("AWS_PRIVATE_SUBNET_IDS"),
    ecr_repo_url=os.getenv("AWS_ECR_REPO_URL"),
    customer_certificate_arn=os.getenv("AWS_CUSTOMER_CERTIFICATE_ARN"),
    customer_apex_domain=os.getenv("AWS_CUSTOMER_APEX_DOMAIN"),
    **env,
)
# print(f"Base Stack Attributes: {base_stack.__dir__()}")

# -------------------------
# Create RDS Aurora Stack -
# -------------------------
# This will provision an Postgres Aurora Cluster and a CMK key.
# rds_stack = RdsStack(
#     app,
#     "RdsStack",
#     base_stack.get_vpc,
#     base_stack.get_subnets,
#     customer_managed_cmk=os.getenv("AWS_KMS_RDS_KEY_ARN"),
#     stack_name=f"{constants.STACK_PREFIX}-rds-stack-{constants.STACK_SUFFIX}",
#     **env,
# )

# ------------------
# Create EFS Stack -
# ------------------
# This will provision an EFS and a CMK key.
# efs_stack = EfsStack(
#     app,
#     "EfsStack",
#     base_stack.get_vpc,
#     base_stack.get_subnets,
#     customer_managed_cmk=os.getenv("AWS_KMS_EFS_KEY_ARN"),
#     stack_name=f"{constants.STACK_PREFIX}-efs-stack-{constants.STACK_SUFFIX}",
#     **env,
# )

# ---------------------
# Create an EKS Stack -
# ---------------------
# This will provision an EKS Fargate Cluster and a CMK key.
eks_stack = EksStack(
    app,
    "EksStack",
    vpc=base_stack.vpc,
    subnets=base_stack.subnets,
    customer_managed_cmk=os.getenv("AWS_KMS_EKS_KEY_ARN"),
    stack_name=f"{constants.STACK_PREFIX}-eks-stack-{constants.STACK_SUFFIX}",
    **env,
)
# print(f"EKS Stack Attributes: {eks_stack.__dir__()}")
eks_stack.add_dependency(base_stack)

# ---------------------
# Create an ALB Stack -
# ---------------------
alb_stack = AlbStack(
    app,
    "AlbStack",
    vpc=base_stack.vpc,
    ecr_repo_url=base_stack.ecr_repo_url,
    eks_cluster=eks_stack.cluster,
    # eks_cluster=eks_stack.get_eks_cluster,
    customer_certificate_arn=base_stack.customer_certificate_arn,
    stack_name=f"{constants.STACK_PREFIX}-alb-stack-{constants.STACK_SUFFIX}",
    **env,
)
# print(f"ALB Stack Attributes: {alb_stack.__dir__()}")
# alb_stack.add_dependency(eks_stack)


# ---------------
# Logging Stack -
# ---------------

# --------------------
# Cert Manager Stack -
# --------------------

# ----------------------
# Network Policy Stack -
# ----------------------

# -------------------
# Application Stack -
# -------------------


# ---------------------
# Synthesize the stacks
# ---------------------
# app.synth()
app.synth(validate_on_synthesis=True, force=True)
