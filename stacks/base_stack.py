from typing import Sequence
from constructs import Construct
from aws_cdk import (
    CfnOutput,
    Duration,
    Stack,
    RemovalPolicy,
    Aws,
    Fn,
    Tags,
    aws_s3 as s3,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_kms as kms,
)
from lib import constants
from stacks import vpc
from stacks.kms import create_kms_key


class BaseStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        vpc_id: str,
        subnet_ids: str,
        ecr_repo_url: str,
        customer_certificate_arn: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)
        # -------------------------------------------------------------------------------------------------------------
        # CUSTOMER INPUTS ---------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------

        # If vpc_id and subnet_ids are provided, we will use those values
        if vpc_id and subnet_ids:
            # We get the VPC type from the provided environment variable
            self.vpc = ec2.Vpc.from_lookup(self, "VPC", vpc_id=vpc_id)

            # We get the subnets type from the provided environment variable
            # Strip any spaces in subnet_ids since it should just be a comma delimited list
            self.subnet_ids = [subnet.strip() for subnet in subnet_ids.split(",")]

            # Perform the lookup/attributes for each subnet ID
            self.subnets = [
                ec2.Subnet.from_subnet_attributes(
                    self, f"Subnet{n}", subnet_id=self.subnet_ids[n]
                )
                for n in range(len(self.subnet_ids))
            ]
        # If DEPLOY_VPC_STACK is set to true, we will create a VPC stack and use the outputs from that stack
        # We want to use this toggle, since we don't want to automatically assume we can create one for the user
        elif constants.DEPLOY_VPC_STACK.lower() == "true":
            self.vpc = vpc.create_vpc(self, "Vpc", **kwargs)
            self.subnets = self.vpc.select_subnets(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ).subnets
        else:
            raise ValueError(
                "Please provide a VPC ID and Subnet IDs or set DEPLOY_VPC_STACK to true to create a VPC stack for you."
            )

        # Sanitize the ECR repo URL the user provides
        self.ecr_repo_url = (
            ecr_repo_url.replace("http://", "").replace("https://", "").rstrip("/")
        )

        self.customer_certificate_arn = customer_certificate_arn

        # -------------------------------------------------------------------------------------------------------------
        # S3 Bucket ---------------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        # Create an S3 bucket with encryption and a lifecycle policy, a strict bucket policy only allowing access to
        # objects from an IAM role that EKS will use. Bucket must be fully private
        self.bucket = s3.Bucket(
            self,
            "bucket",
            access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
            bucket_name=f"{constants.STACK_PREFIX}-bucket",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            lifecycle_rules=[
                s3.LifecycleRule(
                    enabled=True,
                    abort_incomplete_multipart_upload_after=Duration.days(7),
                    expiration=Duration.days(30),
                )
            ],
            removal_policy=RemovalPolicy.DESTROY,
            versioned=True,
        )
        Tags.of(self.bucket).add(
            "Name",
            f"{constants.STACK_PREFIX}-bucket-{constants.STACK_AFFIX}",
        )
        # Create a bucket policy that only allows a specific IAM role to access the bucket
        # The IAM role will be created later
        self.bucket_policy = iam.PolicyStatement(
            actions=[
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket",
                "s3:GetObjectVersion",
                "s3:PutObjectAcl",
                "s3:GetObjectAcl",
                "s3:ListMultipartUploadParts",
                "s3:AbortMultipartUpload",
            ],
            resources=[self.bucket.bucket_arn, self.bucket.arn_for_objects("*")],
            principals=[
                iam.AccountRootPrincipal()
            ],  # TODO: Change this to the EKS role
        )
        self.bucket.add_to_resource_policy(self.bucket_policy)

        # Add a policy statement that denies all principals and s3 actions to the newly created bucket,
        # if aws:SecureTransport is false
        self.bucket_policy_deny = iam.PolicyStatement(
            actions=["s3:*"],
            resources=[self.bucket.bucket_arn, self.bucket.arn_for_objects("*")],
            effect=iam.Effect.DENY,
            principals=[iam.AnyPrincipal()],
            conditions={"Bool": {"aws:SecureTransport": False}},
        )
        self.bucket.add_to_resource_policy(self.bucket_policy_deny)

        # -------------------------------------------------------------------------------------------------------------
        # KMS/CMK Key Creation ----------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        # Create a CMK key for the InitContainer to use to encrypt data
        # We disable key rotation since we don't want to rotate the key
        self.init_cmk_key = create_kms_key(
            self,
            "InitCmk",
            self.region,
            self.account,
            enable_key_rotation=False,
        )
        # -------------------------------------------------------------------------------------------------------------
        # CLOUDFRONT OUTPUTS ------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        CfnOutput(
            self,
            "BucketName",
            value=self.bucket.bucket_name,
            description="Bucket Name for shuffle-tables",
        )
        CfnOutput(self, "BucketArn", value=self.bucket.bucket_arn)
        CfnOutput(self, "VpcId", value=self.vpc.vpc_id, description="VPC ID")
        CfnOutput(
            self,
            "SubnetIds",
            value=Fn.join(",", [subnet.subnet_id for subnet in self.subnets]),
            description="Comma delimited list of subnet IDs",
        )
        CfnOutput(
            self,
            "EcrRepoUrl",
            value=self.ecr_repo_url,
            description="ECR Repo URL",
        )
        CfnOutput(
            self,
            "CertificateArn",
            value=self.customer_certificate_arn,
            description="Certificate ARN",
        )
        CfnOutput(
            self,
            "InitCmkArn",
            value=self.init_cmk_key.key_arn,
            description="Init CMK ARN for application-specific use",
        )

    @property
    def get_bucket(self) -> s3.Bucket:
        return self.bucket

    @property
    def get_bucket_arn(self) -> str:
        return self.bucket.bucket_arn

    @property
    def get_vpc(self) -> ec2.IVpc:
        return self.vpc

    @property
    def get_subnets(self) -> Sequence[ec2.ISubnet]:
        return self.subnets

    @property
    def get_ecr_url(self) -> str:
        return self.ecr_repo_url

    # TODO: if customer does not private a certificate, we will create one using the stacks/certificate.py function
    @property
    def get_customer_certificate_arn(self) -> str:
        return self.customer_certificate_arn

    @property
    def get_init_cmk_key(self) -> kms.Key:
        return self.init_cmk_key
