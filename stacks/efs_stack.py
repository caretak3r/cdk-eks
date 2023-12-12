from constructs import Construct
from aws_cdk import CfnOutput, Duration, Stack, Tags, RemovalPolicy
from aws_cdk import (
    aws_ec2 as ec2,
    aws_efs as efs,
    aws_kms as kms,
    aws_iam as iam,
)
import constants


class EfsStack(Stack):
    def __init__(
        self, scope: Construct, id: str, vpc_id, private_subnet_ids, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # -------------------------------------------------------------------------------------------------------------
        # CUSTOMER INPUTS ---------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        self.vpc_id = vpc_id
        self.private_subnet_ids = private_subnet_ids

        # We get the VPC type from the provided environment variable
        vpc = ec2.Vpc.from_lookup(self, "VPC", vpc_id=self.vpc_id)

        # We get the subnets type from the provided environment variable
        # Strip any spaces in private_subnet_ids since it should just be a comma delimited list
        self.private_subnet_ids = [subnet.strip() for subnet in self.private_subnet_ids]
        subnets = [
            ec2.Subnet.from_subnet_attributes(
                self, f"Subnet{n}", subnet_id=self.private_subnet_ids[n]
            )
            for n in range(len(self.private_subnet_ids))
        ]
        # acknowledge warning: https://github.com/aws/aws-cdk/pull/3171

        # -------------------------------------------------------------------------------------------------------------
        # EFS CREATION ------------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        # Create an EFS filesystem with encryption and a lifecycle policy, a strict filesystem policy only allowing access to objects from an IAM role that EKS will use. Filesystem must be fully private
        self.efs_filesystem = efs.FileSystem(
            self,
            "EFSFileSystem",
            file_system_name=f"{constants.STACK_PREFIX}-efs",
            vpc=vpc,
            kms_key="",
            encrypted=True,
            lifecycle_policy=efs.LifecyclePolicy.AFTER_14_DAYS,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Create a mount target in each private subnet
        for index, subnet in enumerate(vpc.private_subnets, start=1):
            efs.Mount(
                self,
                f"EFSMountTarget{index}",
                file_system=self.efs_filesystem,
                security_groups=[vpc.vpc_default_security_group],
                subnet=subnet,
            )
