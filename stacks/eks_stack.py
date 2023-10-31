from constructs import Construct
from aws_cdk import Stack, CfnOutput, RemovalPolicy, Tags
from aws_cdk import aws_eks as eks, aws_ec2 as ec2, aws_ecr as ecr, aws_logs as logs
from aws_cdk.lambda_layer_kubectl_v27 import KubectlV27Layer
import constants


class EksStack(Stack):
    def __init__(self, scope: Construct, id: str, vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # import existing VPC
        # vpc = ec2.Vpc.from_lookup(self, "VPC", vpc_id=vpc_id) # get this from constants

        # Create a Fargate EKS cluster in the VPC from the VPC Stack
        self.cluster = eks.FargateCluster(
            self,
            "EKSFargateCluster",
            alb_controller=eks.AlbControllerOptions(
                version=eks.AlbControllerVersion.V2_5_1
            ),  # Deploy the ALB controller to the cluster
            cluster_name=f"{constants.STACK_PREFIX}-eks-fargate-cluster",
            cluster_logging=[
                eks.ClusterLoggingTypes.API,
                eks.ClusterLoggingTypes.AUDIT,
                eks.ClusterLoggingTypes.AUTHENTICATOR,
                eks.ClusterLoggingTypes.CONTROLLER_MANAGER,
                eks.ClusterLoggingTypes.SCHEDULER,
            ],
            # core_dns_compute_type=eks.CoreDnsComputeType.FARGATE,  # Use Fargate for CoreDNS
            endpoint_access=eks.EndpointAccess.PUBLIC_AND_PRIVATE,  # Enable public and private access to the cluster endpoint
            kubectl_layer=KubectlV27Layer(
                self, "KubectlV27Layer"
            ),  # Use the kubectl layer created above
            # masters_role=
            output_config_command=True,  # Output the aws eks update-kubeconfig command
            place_cluster_handler_in_vpc=True,  # Place the cluster handler in the VPC
            # role=cluster_admin_role,  # Use the cluster admin role created above (Automatically created for you)
            # security_group=cluster_security_group,  # Use the cluster security group created above (Automatically created for you)
            version=eks.KubernetesVersion.V1_27,
            vpc=vpc,
            vpc_subnets=[
                ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
                {"Name": "Isolated"},
            ],
        )
        Tags.of(self.cluster).add("Name", f"{constants.STACK_PREFIX}EksCluster")

        # Export the cluster name and ARN as stack outputs
        CfnOutput(self, "ClusterName", value=self.cluster.cluster_name)
        CfnOutput(self, "ClusterArn", value=self.cluster.cluster_arn)
        CfnOutput(self, "ClusterEndpoint", value=self.cluster.cluster_endpoint)

        # Logging setup
        log_group = logs.LogGroup(
            self,
            "aws//eks/logs",
            retention=logs.RetentionDays.ONE_WEEK,
            log_group_name=f"{constants.STACK_PREFIX}-EKSStack-log-group",
            removal_policy=RemovalPolicy.DESTROY,
        )
