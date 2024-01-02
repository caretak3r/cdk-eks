from typing import Sequence
from lib import constants
from aws_cdk import (
    CfnOutput,
    Fn,
    Stack,
    Tags,
    aws_ec2 as ec2,
    aws_ecr as ecr,
    aws_eks as eks,
    aws_iam as iam,
    aws_logs as logs,
    aws_kms as kms,
    aws_lambda as lambda_,
)
from aws_cdk.lambda_layer_kubectl_v28 import KubectlV28Layer
from constructs import Construct
from stacks.kms import create_kms_key


class EksStack(Stack):
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
        # IAM Roles ---------------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        control_plane_role = iam.Role(
            self,
            "EksControlPlaneRole",
            assumed_by=iam.ServicePrincipal("eks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonEKSClusterPolicy"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonEKSVPCResourceController"
                ),
            ],
        )
        Tags.of(control_plane_role).add(
            "Name",
            f"{constants.STACK_PREFIX}-eks-control-plane-role-{constants.STACK_AFFIX}",
        )

        masters_role = iam.Role(
            self,
            "MastersRole",
            assumed_by=iam.AccountPrincipal(account_id=self.account),
        )

        # -------------------------------------------------------------------------------------------------------------
        # KMS/CMK Key Creation ----------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        if not customer_managed_cmk:
            self.customer_managed_cmk = create_kms_key(
                self,
                "EksCmk",
                self.region,
                self.account,
                enable_key_rotation=True,
            )
        # -------------------------------------------------------------------------------------------------------------
        # CLUSTER CREATION --------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        # This is required to setup the Kubectl + Helm3 layer and gets passed to the eks.FargateCluster construct
        kubectl_layer = KubectlV28Layer(self, "KubectlV28Layer")

        # Create a Fargate EKS cluster in the VPC from the VPC Stack
        self.cluster = eks.FargateCluster(
            self,
            "EKSFargateCluster",
            cluster_name=f"{constants.STACK_PREFIX}-eks-fargate-cluster-{constants.STACK_AFFIX}",
            cluster_logging=[
                eks.ClusterLoggingTypes.API,
                eks.ClusterLoggingTypes.AUDIT,
                eks.ClusterLoggingTypes.AUTHENTICATOR,
                eks.ClusterLoggingTypes.CONTROLLER_MANAGER,
                eks.ClusterLoggingTypes.SCHEDULER,
            ],
            core_dns_compute_type=eks.CoreDnsComputeType.FARGATE,  # Use Fargate for CoreDNS - default
            endpoint_access=eks.EndpointAccess.PUBLIC_AND_PRIVATE,  # Enable private access to the cluster endpoint
            kubectl_layer=kubectl_layer,
            # masters_role= Automatically created for us
            output_cluster_name=True,  # Output the cluster name
            output_config_command=True,  # Output the aws eks update-kubeconfig command
            output_masters_role_arn=True,  # Output the masters role ARN
            place_cluster_handler_in_vpc=True,  # Place the cluster handler in the VPC
            cluster_handler_environment={"AWS_STS_REGIONAL_ENDPOINTS": "regional"},
            kubectl_environment={"AWS_STS_REGIONAL_ENDPOINTS": "regional"},
            # role=cluster_admin_role,  # Use the cluster admin role created above (Automatically created for you)
            secrets_encryption_key=self.customer_managed_cmk,  # Use the default KMS key
            # security_group=cluster_security_group,  # Use the cluster security group created above (Automatically created for you)
            version=eks.KubernetesVersion.V1_28,
            vpc=vpc,
            vpc_subnets=[ec2.SubnetSelection(subnets=subnets)],
        )
        Tags.of(self.cluster).add(
            "Name",
            f"{constants.STACK_PREFIX}-eks-fargate-cluster-{constants.STACK_AFFIX}",
        )

        print(self.cluster.__dir__())

        # -------------------------------------------------------------------------------------------------------------
        # CLOUDFRONT OUTPUTS ------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        # Export the cluster name and ARN as stack outputs
        CfnOutput(self, "AWS REGION", value=self.region)
        CfnOutput(self, "AWS ACCOUNT ID", value=self.account)
        CfnOutput(
            self,
            "ClusterName",
            value=self.cluster.cluster_name,
            description="EKS Fargate cluster name",
        )
        CfnOutput(
            self,
            "ClusterArn",
            value=self.cluster.cluster_arn,
            description="EKS Fargate cluster ARN",
        )
        CfnOutput(
            self,
            "ClusterEndpoint",
            value=self.cluster.cluster_endpoint,
            description="EKS Fargate cluster endpoint",
        )
        CfnOutput(self, "Vpc-Id", value=vpc.vpc_id, description="VPC ID")
        CfnOutput(
            self, "Vpc-Subnets", value=str(subnets), description="VPC private subnets"
        )
        CfnOutput(
            self,
            "CustomerManagedCmkArn",
            value=self.customer_managed_cmk.key_arn,
            description="Customer Managed CMK for EKS envelope encryption",
        )
        CfnOutput(
            self,
            "SecurityGroupId",
            value=self.cluster.cluster_security_group_id,
            description="Security Group ID",
        )

    @property
    def get_cluster(self) -> eks.Cluster:
        return self.cluster

    @property
    def get_cluster_name(self) -> str:
        return self.cluster.cluster_name

    @property
    def get_customer_managed_cmk(self) -> kms.Key:
        return self.customer_managed_cmk

    @property
    def get_kubectl_role_arn(self) -> str:
        return self.cluster.kubectl_role.role_arn

    @property
    def get_kubectl_lambda_role(self) -> str:
        return self.cluster.kubectl_lambda_role.role_arn

    @property
    def get_oidc_provider_arn(self) -> str:
        return self.cluster.open_id_connect_provider.open_id_connect_provider_arn

    @property
    def get_cluster_security_group_id(self) -> str:
        return self.cluster.cluster_security_group_id
