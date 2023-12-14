import os
from dotenv import load_dotenv, dotenv_values
from aws_cdk import App, Environment
import lib.constants as constants

# from stacks.vpc_stack import VpcStack
from stacks.base_stack import BaseStack
from stacks.eks_stack_mini import EksStack
from stacks.rds_stack import RdsStack
# from stacks.efs_stack import EfsStack
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
# Create a VPC Stack
# -------------------
# If a user wants to deploy a VPC stack, create a VPC stack
# Else, use the VPC ID from the environment variables
# and validate those inputs against the user's AWS Account
# vpc_stack = VpcStack(
#     app,
#     "VpcStack",
#     stack_name=f"{constants.STACK_PREFIX}-vpc-stack-{constants.STACK_AFFIX}",
#     **env,
# )

# --------------------
# Create Base Stack
# --------------------
# This will provision an S3 bucket, and set up values for vpc and subnet_ids.
base_stack = BaseStack(
    app,
    "BaseStack",
    stack_name=f"{constants.STACK_PREFIX}-base-stack-{constants.STACK_AFFIX}",
    vpc_id=os.getenv("AWS_VPC_ID"),
    subnet_ids=os.getenv("AWS_PRIVATE_SUBNET_IDS"),
    ecr_repo_url=os.getenv("AWS_ECR_REPO_URL"),
    certificate_arn=os.getenv("AWS_CERTIFICATE_ARN"),
    **env,
)

# ------------------------
# Create RDS Aurora Stack
# ------------------------
# This will provision an Postgres Aurora Cluster and a CMK key.
# rds_stack = RdsStack(
#     app,
#     "RdsStack",
#     base_stack.get_vpc,
#     base_stack.get_subnets,
#     customer_managed_cmk=os.getenv("AWS_KMS_RDS_KEY_ARN"),
#     stack_name=f"{constants.STACK_PREFIX}-rds-stack-{constants.STACK_AFFIX}",
#     **env,
# )

# --------------------
# Create EFS Stack
# --------------------
# This will provision an EFS and a CMK key.
# efs_stack = EfsStack(
#     app,
#     "EfsStack",
#     base_stack.get_vpc,
#     base_stack.get_subnets,
#     customer_managed_cmk=os.getenv("AWS_KMS_EFS_KEY_ARN"),
#     stack_name=f"{constants.STACK_PREFIX}-efs-stack-{constants.STACK_AFFIX}",
#     **env,
# )

# ------------------------
# Create an EKS Stack Mini
# ------------------------
# This will provision an EKS Fargate Cluster and a CMK key.
eks_stack = EksStack(
    app,
    "EksStack",
    base_stack.get_vpc,
    base_stack.get_subnets,
    customer_managed_cmk=os.getenv("AWS_KMS_EKS_KEY_ARN"),
    # base_stack.get_ecr_url,
    # base_stack.get_certificate_arn,
    stack_name=f"{constants.STACK_PREFIX}-eks-stack-{constants.STACK_AFFIX}",
    **env,
)

# -------------------
# Create an EKS Stack
# -------------------
# eks_stack = EksStack(
#     app,
#     "EksStack",
#     stack_name=f"{constants.STACK_PREFIX}-eks-stack-{constants.STACK_AFFIX}",
#     vpc_id=os.getenv("AWS_VPC_ID"),
#     private_subnet_ids=os.getenv("AWS_PRIVATE_SUBNET_IDS").split(","),
#     certificate_arn=os.getenv("AWS_CERTIFICATE_ARN"),
#     ecr_repo_url=os.getenv("AWS_ECR_REPO_URL"),
#     **env,
# )

# ---------------------
# Synthesize the stacks
# ---------------------
# app.synth()
app.synth(validate_on_synthesis=True, force=True)
