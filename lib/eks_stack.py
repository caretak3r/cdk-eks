from aws_cdk import (
    aws_eks as eks,
    aws_ec2 as ec2,
    aws_ecr as ecr,
    aws_logs as logs,
    core,
)

from aws_cdk.core import App, Construct, Stack
from aws_cdk.aws_eks import Cluster, FargateProfile, KubernetesVersion, Nodegroup
from aws_cdk.aws_lambda_layer_kubectl_v28 import KubectlLayer


class EksStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an EKS cluster within the VPC
        self.cluster = eks.Cluster(
            self,
            "EKSCluster",
            vpc=vpc,
            version=eks.KubernetesVersion.V1_28,
            default_capacity=0,  # we want to manage capacity ourselves
        )

        # Add Fargate profile to EKS cluster
        fargate_profile = eks.FargateProfile(
            self,
            "FargateProfile",
            cluster=self.cluster,  # the EKS cluster to add the profile to
            fargate_profile_name="MyFargateProfile",  # the name of the profile in EKS
            selectors=[
                eks.Selector(namespace="default")
            ],  # the selectors to match for pods to use Fargate
        )

        # Add managed node group to EKS cluster
        self.nodegroup = self.cluster.add_nodegroup_capacity(
            "NodeGroup",
            instance_types=[ec2.InstanceType("t3.medium")],
            desired_size=2,
            max_size=5,
            min_size=1,
        )

        # Export the cluster name and ARN as stack outputs
        core.CfnOutput(self, "ClusterName", value=self.cluster.cluster_name)
        core.CfnOutput(self, "ClusterArn", value=self.cluster.cluster_arn)

        # Export the Fargate profile name and ARN as stack outputs
        core.CfnOutput(
            self, "FargateProfileName", value=fargate_profile.fargate_profile_name
        )
        core.CfnOutput(
            self, "FargateProfileArn", value=fargate_profile.fargate_profile_arn
        )

        # ECR object to apply to EKS cluster- we pull from ECR and apply "something"
        envoy = ecr.Repository.from_repository_name(
            self,
            "aws-envoy",
            repository_arn=core.Stack.of(self).format_arn(
                service="ecr",
                resource="repository",
                resource_name="aws-envoy",
                account="",
            ),
            repository_name="aws-envoy",
        )

        # Logging setup
        log_group = logs.LogGroup(
            self,
            "/eks/logs",
            retention=logs.RetentionDays.ONE_WEEK,
            log_group_name="-eks-log-group",
            removal_policy=core.RemovalPolicy.DESTROY,
        )
