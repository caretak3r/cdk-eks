from constructs import Construct
from aws_cdk import Stack, CfnOutput, RemovalPolicy
from aws_cdk import aws_eks as eks, aws_ec2 as ec2, aws_ecr as ecr, aws_logs as logs
from aws_cdk.lambda_layer_kubectl_v27 import KubectlV27Layer


class EksStack(Stack):
    def __init__(self, scope: Construct, id: str, vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        kubectl_layer = KubectlV27Layer(self, "KubectlV27Layer")

        # Create a Fargate EKS cluster in the VPC from the VPC Stack
        cluster = eks.FargateCluster(
            self,
            "EKSFargateCluster",
            alb_controller=eks.AlbControllerOptions(
                version=eks.AlbControllerVersion.V2_5_1
            ),  # Deploy the ALB controller to the cluster
            cluster_name="EksCdkProjectCluster",
            cluster_logging=[
                eks.ClusterLoggingTypes.API,
                eks.ClusterLoggingTypes.AUDIT,
                eks.ClusterLoggingTypes.AUTHENTICATOR,
                eks.ClusterLoggingTypes.CONTROLLER_MANAGER,
                eks.ClusterLoggingTypes.SCHEDULER,
            ],
            core_dns_compute_type=eks.CoreDnsComputeType.FARGATE,  # Use Fargate for CoreDNS
            endpoint_access=eks.EndpointAccess.PUBLIC_AND_PRIVATE,  # Enable public and private access to the cluster endpoint
            kubectl_layer=kubectl_layer,  # Use the kubectl layer created above
            # masters_role=
            output_config_command=True,  # Output the aws eks update-kubeconfig command
            # role=cluster_admin_role,  # Use the cluster admin role created above (Automatically created for you)
            # security_group=cluster_security_group,  # Use the cluster security group created above (Automatically created for you)
            secrets_encryption_key=eks.SecretsEncryptionKey.KMS,  # Use KMS to encrypt Kubernetes secrets
            version=eks.KubernetesVersion.V1_27,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
        )

        # Export the cluster name and ARN as stack outputs
        CfnOutput(self, "ClusterName", value=self.cluster.cluster_name)
        CfnOutput(self, "ClusterArn", value=self.cluster.cluster_arn)

        # # ECR object to apply to EKS cluster- we pull from ECR and apply "something"
        # envoy = ecr.Repository.from_repository_name(
        #     self,
        #     "aws-envoy",
        #     repository_arn=Stack.of(self).format_arn(
        #         service="ecr",
        #         resource="repository",
        #         resource_name="aws-envoy",
        #         account="",
        #     ),
        #     repository_name="aws-envoy",
        # )

        # pull helm charts from ECR and add_helm_chart() to cluster

        # Logging setup
        log_group = logs.LogGroup(
            self,
            "/eks/logs",
            retention=logs.RetentionDays.ONE_WEEK,
            log_group_name="-eks-log-group",
            removal_policy=RemovalPolicy.DESTROY,
        )
