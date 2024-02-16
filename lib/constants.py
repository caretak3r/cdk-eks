import os
from aws_cdk import (
    Aws,
    CfnOutput,
    Duration,
    Fn,
    RemovalPolicy,
    Stack,
    Tags,
)

# ------------------------------------
# CFN Parameters
# ------------------------------------
STACK_STAGE = os.environ.get("STACK_STAGE", "alpha")
STACK_PREFIX = os.environ.get("STACK_PREFIX", "tkp")
STACK_SUFFIX = os.environ.get("STACK_SUFFIX", "rev11")
STACK_MANAGED_BY = "aws-cdk"
DEPLOY_VPC_STACK = os.environ.get("DEPLOY_VPC_STACK", "true")
AUTHORIZED_ROLE_LIST = ["arn:aws:iam::728168703404:role/token-prowlers-eks-role"]

# ------------------------------------
# EKS Fargate Cluster
# ------------------------------------

# ------------------------------------
# RDS Aurora PostgreSQL Cluster
# ------------------------------------
APP_DATABASE_NAME = os.environ.get("APP_DATABASE_NAME", "")
APP_DATABASE_USERNAME = os.environ.get("APP_DATABASE_USERNAME", "")

# ------------------------------------
# Application Load Balancer
# ------------------------------------

# ------------------------------------
# Cert-Manager
# ------------------------------------
CA_SECRET_NAME = f"{STACK_PREFIX}-cert-manager-ca-secret"
CA_SECRET_REMOVAL_POLICY = RemovalPolicy.DESTROY

# ------------------------------------
# Application Stack
# ------------------------------------
