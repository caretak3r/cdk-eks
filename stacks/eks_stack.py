import json
import os
from lib import constants
from aws_cdk import (
    Aws,
    CfnOutput,
    Fn,
    Stack,
    Tags,
    RemovalPolicy,
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
        vpc_id,
        private_subnet_ids,
        certificate_arn,
        ecr_repo_url,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # -------------------------------------------------------------------------------------------------------------
        # CUSTOMER INPUTS ---------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        self.vpc_id = vpc_id
        self.private_subnet_ids = private_subnet_ids
        self.certificate_arn = certificate_arn
        # Ensure the input is a URI by stripping 'http://' or 'https://' and any trailing '/'
        self.ecr_repo_url = (
            ecr_repo_url.replace("http://", "").replace("https://", "").rstrip("/")
        )

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
        # CLUSTER CREATION --------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        # This is required to setup the Kubectl + Helm3 layer and gets passed to the eks.FargateCluster construct
        kubectl_layer = KubectlV28Layer(self, "KubectlV28Layer")

        # Create a Fargate EKS cluster in the VPC from the VPC Stack
        self.cluster = eks.FargateCluster(
            self,
            "EKSFargateCluster",
            cluster_name=f"{constants.STACK_PREFIX}-eks-fargate-cluster-{constants.STACK_SUFFIX}",
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
            f"{constants.STACK_PREFIX}-eks-fargate-cluster-{constants.STACK_SUFFIX}",
        )

        # TODO: add lib.roles function to enable ec2 masters role

        # -------------------------------------------------------------------------------------------------------------
        # HELM CHART INSTALL: aws-load-balancer-controller ------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
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
        # 2. Creates an IAM policy for the service account
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, "policies/alb-svca-iam-policy.json")
        with open(file_path, mode="r") as file:
            policy_document = json.load(file)

            for statement in policy_document["Statement"]:
                alb_policy_statement = iam.PolicyStatement.from_json(statement)
                alb_service_account.add_to_principal_policy(alb_policy_statement)

        # 3. Creates a Helm chart for the AWS Load  Balancer Controller
        add_alb_chart = self.cluster.add_helm_chart(
            "aws-load-balancer-controller",
            repository=f"oci://{self.ecr_repo_url}/aws-load-balancer-controller-helm-chart",
            chart="aws-load-balancer-controller-helm-chart",
            version="v1.6.2",
            release="aws-load-balancer-controller",
            namespace=alb_service_account.service_account_namespace,
            values={
                "image": {
                    "repository": f"{self.ecr_repo_url}/aws-load-balancer-controller",
                    "tag": "v2.6.2",
                    "pullPolicy": "IfNotPresent",
                },
                "clusterName": self.cluster.cluster_name,
                "serviceAccount": {
                    "create": False,
                    "name": alb_service_account.service_account_name,
                },
                "enableShield": False,
                "enableWaf": False,
                "enableWafv2": False,
                "vpcId": self.vpc_id,
                "logLevel": "debug",
                "defaultTags": {},
                "defaultTargetType": "ip",
            },
        )
        # add_dependency() method is used to add a dependency on the service_account for the helm_chart.
        # This means that the service_account will be created before the helm_chart is deployed.
        add_alb_chart.node.add_dependency(alb_service_account)

        # FIXME: not sure if this needs to go before ALB or after
        # -------------------------------------------------------------------------------------------------------------
        # HELM CHART INSTALL: cert-manager ----------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        # Install cert-manager helm chart from ECR private
        # 1. Creates a Helm chart for the cert-manager
        # add_cert_manager_chart = self.cluster.add_helm_chart(
        #     "cert-manager",
        #     repository=f"oci://{self.ecr_repo_url}/cert-manager-helm-chart",
        #     chart="cert-manager-helm-chart",
        #     version="v1.13.2",
        #     release="cert-manager",
        #     namespace="cert-manager",
        #     values={
        #         "installCRDs": True,
        #         "replicaCount": 2,
        #         "image": {
        #             "repository": f"{self.ecr_repo_url}/cert-manager-controller",
        #             "tag": "v1.13.2",
        #             "pullPolicy": "IfNotPresent",
        #         },
        #         "webhook": {
        #             "securePort": 10260,  # Fargate requirement
        #             "replicaCount": 2,
        #             "image": {
        #                 "repository": f"{self.ecr_repo_url}/cert-manager-webhook",
        #                 "tag": "v1.13.2",
        #                 "pullPolicy": "IfNotPresent",
        #             },
        #         },
        #         "cainjector": {
        #             "enabled": True,
        #             "replicaCount": 2,
        #             "image": {
        #                 "repository": f"{self.ecr_repo_url}/cert-manager-cainjector",
        #                 "tag": "v1.13.2",
        #                 "pullPolicy": "IfNotPresent",
        #             },
        #         },
        #         "acemesolver": {
        #             "enabled": False,
        #         },
        #         "startupapicheck": {
        #             "enabled": False,
        #         },
        #         "prometheus": {
        #             "enabled": False,
        #         },
        #     },
        # )

        # # Create IAM policy for Fluent Bit
        # fluent_bit_policy = iam.Policy(
        #     self,
        #     "FluentBitPolicy",
        #     statements=[
        #         iam.PolicyStatement(
        #             actions=["logs:CreateLogStream", "logs:PutLogEvents"],
        #             resources=["*"],
        #             effect=iam.Effect.ALLOW
        #         )
        #     ]
        # )

        # # Create service account for Fluent Bit
        # fluent_bit_service_account = eks.ServiceAccount(
        #     self,
        #     "FluentBitServiceAccount",
        #     cluster=self.cluster,
        #     name="fluent-bit",
        #     namespace="logging",
        #     policies=[fluent_bit_policy]
        # )

        # # Deploy Fluent Bit manifest
        # fluent_bit_manifest = eks.KubernetesManifest(
        #     self,
        #     "FluentBitManifest",
        #     cluster=self.cluster,
        #     manifest=[
        #         # The Fluent Bit ConfigMap, ServiceAccount, DaemonSet, etc. go here
        #     ]
        # )

        # -------------------------------------------------------------------------------------------------------------
        # HELM CHART INSTALL: http-echo -------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        # Install http-echo helm chart from ECR private
        # 1. Creates a Helm chart for the http-echo
        http_echo_k8s_manifest = self.cluster.add_helm_chart(
            "http-echo",
            repository=f"oci://{self.ecr_repo_url}/http-echo-helm-chart",
            chart="http-echo-helm-chart",
            version="v1.0.0",
            namespace="app",
            values={
                "image": {
                    "repository": f"{self.ecr_repo_url}/http-echo",
                    "tag": "v1.0.0",
                    "pullPolicy": "IfNotPresent",
                },
                "serviceAccount": {"create": False},
                "securityContext": {
                    "allowPrivilegeEscalation": False,
                    "readOnlyRootFilesystem": True,
                    "runAsNonRoot": True,
                },
                "ingress": {
                    "enabled": True,
                    "className": "alb",
                    "annotations": {
                        "kubernetes.io/ingress.class": "alb",
                        "alb.ingress.kubernetes.io/scheme": "internal",
                        "alb.ingress.kubernetes.io/target-type": "ip",
                        "alb.ingress.kubernetes.io/listen-ports": '[{"HTTP": 80}, {"HTTPS": 443}]',
                        "alb.ingress.kubernetes.io/actions.ssl-redirect": (
                            '{"Type": "redirect", "RedirectConfig": {"Protocol": "HTTPS", "Port": "443", "StatusCode": "HTTP_301"}}'
                        ),
                        "alb.ingress.kubernetes.io/certificate-arn": self.certificate_arn,
                    },
                    "hosts": [
                        {
                            "host": "http-echo.tkp.internal",
                            "paths": [
                                {
                                    "path": "/echo",
                                    "pathType": "Exact",
                                    "backend": {
                                        "serviceName": "http-echo",
                                        "servicePort": 5678,
                                    },
                                }
                            ],
                        }
                    ],
                },
            },
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
        CfnOutput(self, "Vpc-Id", value=vpc_id)
        CfnOutput(self, "Subnet-Ids", value=Fn.join(",", private_subnet_ids))
        CfnOutput(self, "CertificateArn", value=self.certificate_arn)
        CfnOutput(self, "ECRRepoURL", value=self.ecr_repo_url)

        # CfnOutput(self, "CustomerManagedKeyArn", value=self.customer_managed_key_arn)
        CfnOutput(
            self,
            "ALBServiceAccountName",
            value=alb_service_account.service_account_name,
        )
        CfnOutput(
            self,
            "ALBServiceAccountNamespace",
            value=alb_service_account.service_account_namespace,
        )
