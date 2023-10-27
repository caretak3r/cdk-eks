from constructs import Construct
from aws_cdk import CfnOutput, Duration, Stack, Tags, RemovalPolicy
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as ecr
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

        # Configure the target ECR repository, or create if a name was provided.
        if isinstance(ecr_repo, ecr.Repository):
            self.repo = ecr_repo
        else:
            self.repo = ecr.Repository(
                self,
                "EcrRepo",
                image_scan_on_push=True,
                repository_name=f"{constants.STACK_PREFIX}-EcrRepo",
                removal_policy=RemovalPolicy.DESTROY,
                encryption=ecr.RepositoryEncryption.AES_256,
            )

        CfnOutput(
            self,
            "EcrRepo",
            value=self.repo.repository_name,
            description="The name of the ECR repository",
        )
