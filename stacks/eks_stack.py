from constructs import Construct
from aws_cdk import Stack, CfnOutput, RemovalPolicy, Tags, CfnParameter, Fn, Reference
from aws_cdk import aws_eks as eks, aws_ec2 as ec2, aws_ecr as ecr, aws_logs as logs
from aws_cdk.lambda_layer_kubectl_v27 import KubectlV27Layer
import constants


class EksStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        kubectl_layer = KubectlV27Layer(self, "KubectlV27Layer")

        # Allow user to pass in parameters in the synthesized cloudformation template
        vpc_id_param = CfnParameter(
            self,
            "VpcId",
            type="AWS::EC2::VPC::Id",
            description="Please select the ID of the VPC we will deploy to.",
            constraint_description="must be a valid VPC ID.",
        ).value_as_string

        subnet_ids_param = CfnParameter(
            self,
            "SubnetIds",
            type="List<AWS::EC2::Subnet::Id>",
            description="Please select at least 2 IDs for the private isolated subnets.",
            constraint_description="must be a valid list of subnet IDs.",
        ).value_as_list

        vpc_subnets = ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED)

        # Create a Fargate EKS cluster in the VPC from the VPC Stack
        self.cluster = eks.FargateCluster(
            self,
            "EKSFargateCluster",
            # In order to access applications inside the clusters from the internet,
            # the cluster needs the ability to provision on-demand AWS load balancers that
            # route to internal Kubernetes resources.
            # (see https://github.com/aws/aws-cdk/tree/main/packages/aws-cdk-lib/aws-eks#alb-controller)
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
            endpoint_access=eks.EndpointAccess.PRIVATE,  # Enable public and private access to the cluster endpoint
            # In addition, the `eks.Cluster` construct is able to apply Kubernetes manifests onto the
            # cluster (we will use that capability later) via the `kubectl` utility.
            # Kubernetes recommends to always match the version of `kubectl` to the version of your
            # cluster.
            kubectl_layer=kubectl_layer,
            # masters_role= Automatically created for us
            output_config_command=True,  # Output the aws eks update-kubeconfig command
            place_cluster_handler_in_vpc=True,  # Place the cluster handler in the VPC
            # role=cluster_admin_role,  # Use the cluster admin role created above (Automatically created for you)
            # security_group=cluster_security_group,  # Use the cluster security group created above (Automatically created for you)
            version=eks.KubernetesVersion.V1_27,
            vpc=vpc_id_param,
            vpc_subnets=vpc_subnets,
        )
        Tags.of(self.cluster).add(
            "Name", f"{constants.STACK_PREFIX}-eks-fargate-cluster"
        )

        # Kubernetes clusters often contain common middleware that has cross-application concerns
        # such as observability, certificate management, and more. Such middleware can be easily
        # installed with [helm](https://helm.sh/), which is natively supported by the `eks.Cluster` construct.
        # In this example, we install KubeView, a visualizer that helps you understand the relationships
        # between Kubernetes resources in your cluster.
        # (see https://artifacthub.io/packages/helm/kubeview/kubeview)
        if constants.INSTALL_HELM_CHARTS:
            self.cluster.add_helm_chart(
                "KubeView",
                repository="https://benc-uk.github.io/kubeview/charts",
                chart="kubeview",
                namespace="kube-system",
                values={
                    # control the service name since we will need to
                    # reference to it from our app
                    "fullnameOverride": "kubeview"
                },
            )
            # Kubeview is exposed via an ELB, and to access it, we need to fetch its generated DNS address.
            # The address is stored in the state of the Kubernetes service that is backed by the ELB, and
            # can be fetched using the `getServiceLoadBalancerAddress` method:
            kube_view_address = self.cluster.get_service_load_balancer_address(
                "kubeview", namespace="kube-system"
            )
            # We also define a CloudFormation output for this value, so that we can see it once
            # deployment finishes successfully.
            CfnOutput(self, "KubeViewEndpoint", value=f"http://{kube_view_address}")

        # Export the cluster name and ARN as stack outputs
        CfnOutput(self, "ClusterName", value=self.cluster.cluster_name)
        CfnOutput(self, "ClusterArn", value=self.cluster.cluster_arn)
        CfnOutput(self, "ClusterEndpoint", value=self.cluster.cluster_endpoint)
        CfnOutput(self, "Vpc-Id", value=vpc_id_param)
        CfnOutput(self, "Subnet-Ids", value=Fn.join(",", subnet_ids_param))

        # Logging setup
        logs.LogGroup(
            self,
            "aws/eks/logs",
            retention=logs.RetentionDays.ONE_WEEK,
            log_group_name=f"{constants.STACK_PREFIX}-eks-cluster-log-group",
            removal_policy=RemovalPolicy.DESTROY,
        )
        # TODO: configure a proper rentention policy for the log group
        # TODO: add a data protection policy
        # TODO: add a description to the log group
