from typing import Sequence

from aws_cdk import CfnOutput, Duration, RemovalPolicy, Stack, Tags
from aws_cdk import (
    aws_ec2 as ec2,
)
from aws_cdk import (
    aws_kms as kms,
)
from aws_cdk import (
    aws_logs as logs,
)
from aws_cdk import (
    aws_rds as rds,
)
from aws_cdk import (
    aws_secretsmanager as secrets,
)
from constructs import Construct

from lib import constants
from stacks.kms import create_kms_key


class RdsStack(Stack):
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
        # KMS: If customer does not provide a customer managed key, we will create one using the stacks/kms.py function
        if not customer_managed_cmk:
            self.customer_managed_cmk = create_kms_key(
                self,
                "RdsKms",
                self.region,
                self.account,
                enable_key_rotation=True,
            )

        # -------------------------------------------------------------------------------------------------------------
        # RDS CLUSTER CREATION ----------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        # Create security group for RDS
        db_security_group = ec2.SecurityGroup(
            self,
            "db-security-group",
            vpc=vpc,
            allow_all_outbound=False,
            description="Security group for RDS",
            security_group_name=f"{constants.STACK_PREFIX}-db-security-group",
        )

        db_security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(
                vpc.vpc_cidr_block
            ),  # allows ingress from VPC CIDR ranges
            connection=ec2.Port.tcp(5432),  # default postgres port 5432
            description="INGRESS Private communication between RDS and EKS",
        )

        db_security_group.add_egress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.all_tcp(),
            description="EGRESS Private communication between RDS and EKS",
        )

        # Create a PostgreSQL Aurora cluster
        self.cluster = rds.DatabaseCluster(
            self,
            "AuroraCluster",
            engine=rds.DatabaseClusterEngine.aurora_postgres(
                version=rds.AuroraPostgresEngineVersion.VER_14_6
            ),
            cluster_identifier=f"{constants.STACK_PREFIX}-aurora-cluster",
            # credentials=aurora_cluster_credentials,
            cloudwatch_logs_exports=["postgresql"],
            cloudwatch_logs_retention=logs.RetentionDays.ONE_MONTH,
            default_database_name=f"{constants.APP_DATABASE_NAME}",
            deletion_protection=True,
            parameter_group=rds.ParameterGroup.from_parameter_group_name(
                self,
                "ParameterGroup",
                parameter_group_name="default.aurora-postgresql14",
            ),
            # preferred_maintenance_window=  30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week. #TODO set this
            removal_policy=RemovalPolicy.SNAPSHOT,  # takes a snapshot before removal
            copy_tags_to_snapshot=True,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnets=subnets),
            security_groups=[db_security_group],
            subnet_group=rds.SubnetGroup(
                self,
                id=f"{constants.STACK_PREFIX}-AuroraSubnetGroup",
                vpc=vpc,
                description=id + " Subnet group for RDS",
                vpc_subnets=ec2.SubnetSelection(subnets=subnets),
                subnet_group_name=id + "-SubnetGroup",
            ),
            storage_encrypted=True,
            storage_encryption_key=self.customer_managed_cmk,
            writer=rds.ClusterInstance.provisioned(
                "writer",
                publicly_accessible=False,
                instance_type=ec2.InstanceType.of(
                    ec2.InstanceClass.R5, ec2.InstanceSize.LARGE
                ),
            ),
            readers=[
                rds.ClusterInstance.provisioned(
                    "reader",
                    instance_type=ec2.InstanceType.of(
                        ec2.InstanceClass.R5, ec2.InstanceSize.LARGE
                    ),
                )
            ],
            storage_type=rds.DBClusterStorageType.AURORA,
        )

        # publish logs to cloudwatch logs
        logs.LogGroup(
            self,
            "aws/rds/logs",
            retention=logs.RetentionDays.ONE_MONTH,
            log_group_name=f"{constants.STACK_PREFIX}-rds-cluster-log-group",
            removal_policy=RemovalPolicy.DESTROY,
        )

        CfnOutput(
            self,
            "RdsClusterIdentifier",
            value=self.cluster.cluster_identifier,
            description="RDS Cluster Identifier",
            export_name="RdsClusterIdentifier",
        )
        CfnOutput(
            self,
            "RdsClusterResourceIdentifier",
            value=self.cluster.cluster_resource_identifier,
            description="RDS Cluster Resource Identifier",
        )
        CfnOutput(
            self,
            "RdsClusterEndpoint",
            value=self.cluster.cluster_endpoint.hostname,
            description="RDS Cluster Endpoint",
        )
