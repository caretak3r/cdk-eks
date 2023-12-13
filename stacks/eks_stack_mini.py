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
)
from aws_cdk.lambda_layer_kubectl_v28 import KubectlV28Layer
from constructs import Construct


class EksStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        vpc: ec2.IVpc,
        subnets: Sequence[ec2.ISubnet],
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

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
            output_config_command=True,  # Output the aws eks update-kubeconfig command
            place_cluster_handler_in_vpc=True,  # Place the cluster handler in the VPC
            cluster_handler_environment={"AWS_STS_REGIONAL_ENDPOINTS": "regional"},
            kubectl_environment={"AWS_STS_REGIONAL_ENDPOINTS": "regional"},
            # role=cluster_admin_role,  # Use the cluster admin role created above (Automatically created for you)
            # secrets_encryption_key = eks.SecretsEncryptionKey.KMS,  # Use the default KMS key
            # security_group=cluster_security_group,  # Use the cluster security group created above (Automatically created for you)
            version=eks.KubernetesVersion.V1_28,
            vpc=vpc,
            vpc_subnets=[ec2.SubnetSelection(subnets=subnets)],
        )
        Tags.of(self.cluster).add(
            "Name",
            f"{constants.STACK_PREFIX}-eks-fargate-cluster-{constants.STACK_AFFIX}",
        )

        # -------------------------------------------------------------------------------------------------------------
        # CLOUDFRONT OUTPUTS ------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        # Export the cluster name and ARN as stack outputs
        CfnOutput(self, "AWS REGION", value=self.region)
        CfnOutput(self, "AWS ACCOUNT ID", value=self.account)
        CfnOutput(self, "ClusterName", value=self.cluster.cluster_name)
        CfnOutput(self, "ClusterArn", value=self.cluster.cluster_arn)
        CfnOutput(self, "ClusterEndpoint", value=self.cluster.cluster_endpoint)
        CfnOutput(self, "Vpc-Id", value=vpc.vpc_id)
