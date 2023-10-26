from constructs import Construct
from aws_cdk import Stack, CfnOutput, Tags, Fn, Aws
from aws_cdk import (
    aws_eks as eks,
    aws_ec2 as ec2,
    aws_ecr as ecr,
    aws_logs as logs,
    aws_iam as iam,
)
from aws_cdk.lambda_layer_kubectl_v27 import KubectlV27Layer
import constants
import os
import json


class EksStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        vpc_id,
        private_subnet_ids,
        certificate_arn,
        ecr_repo_url,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        self.vpc_id = vpc_id
        self.private_subnet_ids = private_subnet_ids
        self.certificate_arn = certificate_arn
        self.ecr_repo_url = ecr_repo_url

        # This is required to setup the Kubectl + Helm3 layer and gets passed to the eks.FargateCluster construct
        kubectl_layer = KubectlV27Layer(self, "KubectlV27Layer")

        # We get the VPC type from the provided environment variable
        vpc = ec2.Vpc.from_lookup(self, "VPC", vpc_id=self.vpc_id)
        # TODO: we should tag the VPC and subnets since the customer won't, look at vpc_stack.py
        # TODO:  Please note when using an existing VPC, please make sure its private subnets have been tagged with "kubernetes.io/role/internal-elb: 1"

        # We get the subnets type from the provided environment variable
        subnets = [
            ec2.Subnet.from_subnet_attributes(
                self, f"Subnet{n}", subnet_id=self.private_subnet_ids[n]
            )
            for n in range(len(self.private_subnet_ids))
        ]
        # acknowledge warning: https://github.com/aws/aws-cdk/pull/3171

        # Create a Fargate EKS cluster in the VPC from the VPC Stack
        self.cluster = eks.FargateCluster(
            self,
            "EKSFargateCluster",
            # This ONLY WORKS if VPC has a route to the public internet. Otherwise we deploy the ALB controller manually.
            # In order to access applications inside the clusters from the internet,
            # the cluster needs the ability to provision on-demand AWS load balancers that
            # route to internal Kubernetes resources.
            # (see https://github.com/aws/aws-cdk/tree/main/packages/aws-cdk-lib/aws-eks#alb-controller)
            # alb_controller=eks.AlbControllerOptions(
            #     version=eks.AlbControllerVersion.V2_5_4
            # ),  # Deploy the ALB controller to the cluster
            cluster_name=f"{constants.STACK_PREFIX}-eks-fargate-cluster-{constants.STACK_AFFIX}",
            cluster_logging=[
                eks.ClusterLoggingTypes.API,
                eks.ClusterLoggingTypes.AUDIT,
                eks.ClusterLoggingTypes.AUTHENTICATOR,
                eks.ClusterLoggingTypes.CONTROLLER_MANAGER,
                eks.ClusterLoggingTypes.SCHEDULER,
            ],
            core_dns_compute_type=eks.CoreDnsComputeType.FARGATE,  # Use Fargate for CoreDNS - default
            endpoint_access=eks.EndpointAccess.PUBLIC_AND_PRIVATE,  # Enable public and private access to the cluster endpoint #TODO: test PRIVATE only
            kubectl_layer=kubectl_layer,
            # masters_role= Automatically created for us
            output_config_command=True,  # Output the aws eks update-kubeconfig command
            place_cluster_handler_in_vpc=True,  # Place the cluster handler in the VPC
            cluster_handler_environment={"AWS_STS_REGIONAL_ENDPOINTS": "regional"},
            kubectl_environment={"AWS_STS_REGIONAL_ENDPOINTS": "regional"},
            # role=cluster_admin_role,  # Use the cluster admin role created above (Automatically created for you)
            # secrets_encryption_key = eks.SecretsEncryptionKey.KMS,  # Use the default KMS key
            # security_group=cluster_security_group,  # Use the cluster security group created above (Automatically created for you)
            version=eks.KubernetesVersion.V1_27,
            vpc=vpc,
            vpc_subnets=[ec2.SubnetSelection(subnets=subnets)],
        )
        Tags.of(self.cluster).add(
            "Name",
            f"{constants.STACK_PREFIX}-eks-fargate-cluster-{constants.STACK_AFFIX}",
        )

        # IAM mapping
        self.add_admin_role_to_cluster()
        self.add_cluster_admin()

        authorized_role_list = ['']
        # add permissions to iam user so see the cluster
        for user in authorized_role_list:
            auth_user = iam.User.from_user_name(self, "MyImportedUserByName", user)
            self.cluster.aws_auth.add_role_mapping(auth_user, groups=["system:masters"])

        # Install AWS Load Balancer Controller since we can't use the eks.Cluster construct's alb_controller option
        # since it needs the internet to download. We source from ECR private instead.

        # 1. Creates and Service account for our cluster to add a load Balancer
        alb_service_account = eks.ServiceAccount(
            self,
            "ALBServiceAccount",
            cluster=self.cluster,
            name="aws-load-balancer-controller",
            namespace="kube-system",
        )


        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, "alb-svca-iam-policy.json")
        with open(file_path, mode="r") as file:
            policy_document = json.load(file)

            for statement in policy_document["Statement"]:
                alb_policy_statement = iam.PolicyStatement.from_json(statement)
                alb_service_account.add_to_principal_policy(alb_policy_statement)

        # 2. Creates a Helm chart for the AWS Load  Balancer Controller
        add_alb_chart = self.cluster.add_helm_chart(
            "aws-load-balancer-controller",
            repository=f"oci://{self.ecr_repo_url}",
            chart="platform",
            version="1.6.2-aws-load-balancer-controller-helm-chart",
            release="aws-load-balancer-controller",
            namespace=alb_service_account.service_account_namespace,
            values={
                "clusterName": self.cluster.cluster_name,
                "serviceAccount": {
                    "create": False,
                    "name": alb_service_account.service_account_name,
                },
                "enableShield": False,
                "enableWaf": False,
                "enableWafv2": False,
            },
        )

        print(add_alb_chart.to_string())

        add_alb_chart.node.add_dependency(alb_service_account)

        # TODO: add IAM role mapping to the cluster to view it

        # self.cluster.add_fargate_profile(
        #     "ObservabilityProfile",
        #     selectors=[
        #         eks.Selector(
        #             namespace="observability",
        #             labels={"app.kubernetes.io/name": "kubeview"},
        #         )
        #     ],
        # )

        # Kubernetes clusters often contain common middleware that has cross-application concerns
        # such as observability, certificate management, and more. Such middleware can be easily
        # installed with [helm](https://helm.sh/), which is natively supported by the `eks.Cluster` construct.
        # In this example, we install KubeView, a visualizer that helps you understand the relationships
        # between Kubernetes resources in your cluster.
        # (see https://artifacthub.io/packages/helm/kubeview/kubeview)
        # self.cluster.add_helm_chart(
        #     "KubeView",
        #     repository="https://benc-uk.github.io/kubeview/charts",
        #     chart="kubeview",
        #     namespace="kube-system",
        #     values={
        #         # control the service name since we will need to
        #         # reference to it from our app
        #         "fullnameOverride": "kubeview"
        #     },
        # )
        # # Kubeview is exposed via an ELB, and to access it, we need to fetch its generated DNS address.
        # # The address is stored in the state of the Kubernetes service that is backed by the ELB, and
        # # can be fetched using the `getServiceLoadBalancerAddress` method:
        # kube_view_address = self.cluster.get_service_load_balancer_address(
        #     "kubeview", namespace="kube-system"
        # )
        # # We also define a CloudFormation output for this value, so that we can see it once
        # # deployment finishes successfully.
        # CfnOutput(self, "KubeViewEndpoint", value=f"http://{kube_view_address}")

        # Export the cluster name and ARN as stack outputs
        CfnOutput(self, "AWS REGION", value=self.region)
        CfnOutput(self, "AWS ACCOUNT ID", value=self.account)
        CfnOutput(self, "ClusterName", value=self.cluster.cluster_name)
        CfnOutput(self, "ClusterArn", value=self.cluster.cluster_arn)
        CfnOutput(self, "ClusterEndpoint", value=self.cluster.cluster_endpoint)
        CfnOutput(self, "Vpc-Id", value=vpc_id)
        CfnOutput(self, "Subnet-Ids", value=Fn.join(",", private_subnet_ids))

        # # Logging setup
        # logs.LogGroup(
        #     self,
        #     "aws/eks/logs",
        #     retention=logs.RetentionDays.ONE_WEEK,
        #     log_group_name=f"{constants.STACK_PREFIX}-eks-cluster-log-group",
        #     removal_policy=RemovalPolicy.DESTROY,
        # )
        # TODO: configure a proper rentention policy for the log group
        # TODO: add a data protection policy
        # TODO: add a description to the log group

    def add_admin_role_to_cluster(self) -> None:
        admin_role_name = self.node.try_get_context("eks_admin_role_name")
        if admin_role_name is None:
            return

        account_id = Aws.ACCOUNT_ID
        admin_role = iam.Role.from_role_arn(
            self, "admin_role", f"arn:aws:iam::{account_id}:role/{admin_role_name}"
        )
        self.cluster.aws_auth.add_masters_role(admin_role)

    def add_cluster_admin(self, name="eks-admin"):
    # Add admin privileges so we can sign in to the dashboard as the service account
        sa = self.cluster.add_manifest(
            "eks-admin-sa",
            {
                "apiVersion": "v1",
                "kind": "ServiceAccount",
                "metadata": {
                    "name": name,
                    "namespace": "kube-system",
                },
            },
        )
        binding = self.cluster.add_manifest(
            "eks-admin-rbac",
            {
                "apiVersion": "rbac.authorization.k8s.io/v1beta1",
                "kind": "ClusterRoleBinding",
                "metadata": {"name": name},
                "roleRef": {
                    "apiGroup": "rbac.authorization.k8s.io",
                    "kind": "ClusterRole",
                    "name": "cluster-admin",
                },
                "subjects": [
                    {
                        "kind": "ServiceAccount",
                        "name": name,
                        "namespace": "kube-system",
                    }
                ],
            },
        )