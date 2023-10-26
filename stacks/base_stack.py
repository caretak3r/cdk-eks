from constructs import Construct
from aws_cdk import CfnOutput, Duration, Stack, RemovalPolicy
from aws_cdk import aws_ecr as ecr, aws_s3 as s3, aws_iam as iam
import constants
from typing import Union


class BaseStack(Stack):
    def __init__(
        self, scope: Construct, id: str, ecr_repo: Union[str, ecr.Repository], **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # Configure the target ECR repository, or create if a name was provided.
        if isinstance(ecr_repo, ecr.Repository):
            self.repo = ecr_repo
        else:
            self.repo = ecr.Repository(
                self,
                "ecrrepo",
                image_scan_on_push=True,
                repository_name=f"{constants.STACK_PREFIX}-ecrrepo",
                removal_policy=RemovalPolicy.DESTROY,
                encryption=ecr.RepositoryEncryption.AES_256,
            )

        CfnOutput(
            self,
            "ecrrepo1",
            value=self.repo.repository_name,
            description="The name of the ECR repository",
        )

        # Create an S3 bucket with encryption and a lifecycle policy, a strict bucket policy only allowing access to objects from an IAM role that EKS will use. Bucket must be fully private
        # separate bucket into its own stack since it depends on the EKS role created #TODO
        # otherwise create a specific IAM role for the master role, which is deterministic and keep the s3 bucket in this stack
        self.bucket = s3.Bucket(
            self,
            "bucket",
            bucket_name=f"{constants.STACK_PREFIX}-bucket",
            encryption=s3.BucketEncryption.KMS_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            lifecycle_rules=[
                s3.LifecycleRule(
                    enabled=True,
                    abort_incomplete_multipart_upload_after=Duration.days(7),
                    expiration=Duration.days(30),
                )
            ],
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.bucket_policy = iam.PolicyStatement(
            actions=["s3:GetObject", "s3:PutObject"],
            resources=[self.bucket.arn_for_objects("*")],
            principals=[
                iam.Role.from_role_arn(
                    self, "Role", "arn:aws:iam::123456789012:role/eks"
                )
            ],
        )
        self.bucket.add_to_resource_policy(self.bucket_policy)
