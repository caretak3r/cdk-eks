from constructs import Construct
from aws_cdk import CfnOutput, Duration, Stack, RemovalPolicy
from aws_cdk import aws_s3 as s3, aws_iam as iam
import constants


class BaseStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an S3 bucket with encryption and a lifecycle policy, a strict bucket policy only allowing access to objects from an IAM role that EKS will use. Bucket must be fully private
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

        CfnOutput(self, "bucket_name", value=self.bucket.bucket_name)
        CfnOutput(self, "bucket_arn", value=self.bucket.bucket_arn)
