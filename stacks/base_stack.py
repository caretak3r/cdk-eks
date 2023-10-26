from constructs import Construct
from aws_cdk import CfnOutput, Duration, Stack, Tags
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_logs as logs
from aws_cdk import aws_kms as kms
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_ssm as ssm
from aws_cdk import aws_iam as iam
import constants


# This stack will deploy a VPC with private subnets and no internet gateways or NAT gateways, a KMS key with an alias to encrypt EKS, and an S3 bucket that is completely private, and Cloudwatch log groups, and any IAM roles. Every resource will have an output with CfnOutput.
class BaseStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
