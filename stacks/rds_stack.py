from constructs import Construct
from aws_cdk import CfnOutput, Duration, Stack, Tags, RemovalPolicy
from aws_cdk import (
    aws_ec2 as ec2,
    aws_logs as logs,
    aws_kms as kms,
    aws_rds as rds,
    aws_iam as iam,
)
import constants


class RdsStack(Stack):
    def __init__(
        self, scope: Construct, id: str, vpc: ec2.Vpc, subnets: ec2.ISubnet, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # import existing VPC and find the subnets to use to deploy RDS and subnet_groups
        vpc_subnets = ec2.SubnetSelection(subnets=subnets)

        # Create a KMS key specifcally for RDS
        # TODO: reeval the retention of the key in use
        self.kms_key = kms.Key(
            self,
            "KmsKey",
            removal_policy=RemovalPolicy.DESTROY,
            description="KMS key for RDS encryption",
            alias=f"alias/{constants.STACK_PREFIX}-kms-key",
            enabled=True,
            enable_key_rotation=True,
            pending_window=Duration.days(7),
        )

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
            connection=ec2.Port.tcp(5432),  # default postgres port
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
                version=rds.AuroraPostgresEngineVersion.VER_15_3
            ),
            cluster_identifier=f"{constants.STACK_PREFIX}-aurora-cluster",
            cloudwatch_logs_exports=["postgresql"],
            cloudwatch_logs_retention=logs.RetentionDays.ONE_MONTH,
            default_database_name="DefaultDB",
            deletion_protection=True,
            iam_authentication=True,
            parameter_group=rds.ParameterGroup.from_parameter_group_name(
                self,
                "ParameterGroup",
                parameter_group_name="default.aurora-postgresql15",
            ),
            # preferred_maintenance_window=  30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week. #TODO set this
            removal_policy=RemovalPolicy.SNAPSHOT,  # takes a snapshot before removal
            copy_tags_to_snapshot=True,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            security_groups=[db_security_group],
            subnet_group=rds.SubnetGroup(
                self,
                id=f"{constants.STACK_PREFIX}-SubnetGroup",
                vpc=vpc,
                description=id + " Subnet group for RDS",
                vpc_subnets=vpc_subnets,
                subnet_group_name=id + "-SubnetGroup",
            ),
            storage_encrypted=True,
            storage_encryption_key=self.kms_key,
            writer=rds.ClusterInstance.provisioned(
                "writer",
                publicly_accessible=False,
                instance_type=ec2.InstanceType.of(
                    ec2.InstanceClass.R6G, ec2.InstanceSize.XLARGE4
                ),
            ),
            readers=[rds.ClusterInstance.provisioned("reader")],
            storage_type=rds.DBClusterStorageType.AURORA_IOPT1,
        )

        # TODO: ensure backup policy via AWS Backup is in place or upload backups to s3 with minimal retention
        # don't know how long if needed, backups should be retained.

        # publish logs to cloudwatch logs
        logs.LogGroup(
            self,
            "aws/rds/logs",
            retention=logs.RetentionDays.ONE_MONTH,
            log_group_name=f"{constants.STACK_PREFIX}-rds-cluster-log-group",
            removal_policy=RemovalPolicy.DESTROY,
        )
