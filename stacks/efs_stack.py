from constructs import Construct
from aws_cdk import CfnOutput, Duration, Stack, Tags, RemovalPolicy
from aws_cdk import (
    aws_ec2 as ec2,
    aws_efs as efs,
    aws_kms as kms,
    aws_iam as iam,
)
from lib import constants
from typing import Sequence
from stacks.kms import create_kms_key


class EfsStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        vpc: ec2.IVpc,
        subnets: Sequence[ec2.ISubnet],
        customer_managed_cmk: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)
        # -------------------------------------------------------------------------------------------------------------
        # KMS/CMK Key Creation ----------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        if not customer_managed_cmk:
            self.customer_managed_cmk = create_kms_key(
                self,
                "EfsCmk",
                self.region,
                self.account,
                enable_key_rotation=True,
            )
        # -------------------------------------------------------------------------------------------------------------
        # EFS CREATION ------------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        # Create an EFS filesystem with encryption and a lifecycle policy, a strict filesystem policy only allowing access to objects from an IAM role that EKS will use. Filesystem must be fully private
        self.efs_filesystem = efs.FileSystem(
            self,
            "EFSFileSystem",
            file_system_name=f"{constants.STACK_PREFIX}-efs",
            vpc=vpc,
            kms_key=customer_managed_cmk,
            encrypted=True,
            performance_mode=efs.PerformanceMode.GENERAL_PURPOSE,  # default
            lifecycle_policy=efs.LifecyclePolicy.AFTER_14_DAYS,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Create a mount target in each private subnet

        # TODO: what needs to be done to allow any fargate pod to mount a volume/
        # more specifically only the application pods that need to mount the volume
