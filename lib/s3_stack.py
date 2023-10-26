from aws_cdk import aws_s3 as s3
from constructs import Construct
from aws_cdk import Stack, CfnOutput, Duration
import constants


class S3Stack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs: str) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an S3 bucket
        self.bucket = s3.Bucket(
            self,
            id=f"{constants.STACK_PREFIX}S3Bucket",
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=True,
                block_public_policy=True,
                ignore_public_acls=True,
                restrict_public_buckets=True,
            ),
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="CleaningUp",
                    enabled=True,
                    expiration=Duration.days(1),
                    abort_incomplete_multipart_upload_after=Duration.days(1),
                ),
            ],
            versioned=True,
        )
        CfnOutput(
            self,
            "BucketName",
            value=self.bucket.bucket_name,
        )

    @property
    def get_bucket(self) -> s3.Bucket:
        return self.bucket
