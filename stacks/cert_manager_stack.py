from constructs import Construct
from aws_cdk import (
    CfnOutput,
    Duration,
    Stack,
    RemovalPolicy,
    Aws,
    Fn,
    Tags,
    aws_eks as eks,
)
from lib import constants


class CertManagerStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        ecr_repo_url: str,
        cluster_name: str,
        kubectl_role_arn: str,
        customer_certificate_arn: str,
        open_id_connect_provider_arn: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.ecr_repo_url = ecr_repo_url
        self.customer_certificate_arn = customer_certificate_arn

        # EKS Cluster is used throughout the stack
        self.cluster = eks.Cluster.from_cluster_attributes(
            self,
            "ImportedEksCluster",
            cluster_name=cluster_name,
            kubectl_role_arn=kubectl_role_arn,
            open_id_connect_provider=eks.OpenIdConnectProvider.from_open_id_connect_provider_arn(
                self,
                "ImportedOpenIdConnectProvider",
                open_id_connect_provider_arn=open_id_connect_provider_arn,
            ),
        )

        # -------------------------------------------------------------------------------------------------------------
        # HELM CHART INSTALL: cert-manager ----------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        # Install cert-manager helm chart from ECR private
        # 1. Creates a Helm chart for the cert-manager
        add_cert_manager_chart = self.cluster.add_helm_chart(
            "cert-manager",
            repository=f"oci://{self.ecr_repo_url}/cert-manager-helm-chart",
            chart="cert-manager-helm-chart",
            version="v1.13.2",
            release="cert-manager",
            namespace="cert-manager",
            values={
                "installCRDs": True,
                "replicaCount": 2,
                "image": {
                    "repository": f"{self.ecr_repo_url}/cert-manager-controller",
                    "tag": "v1.13.2",
                    "pullPolicy": "IfNotPresent",
                },
                "webhook": {
                    "securePort": 10260,  # Fargate requirement
                    "replicaCount": 2,
                    "image": {
                        "repository": f"{self.ecr_repo_url}/cert-manager-webhook",
                        "tag": "v1.13.2",
                        "pullPolicy": "IfNotPresent",
                    },
                },
                "cainjector": {
                    "enabled": True,
                    "replicaCount": 2,
                    "image": {
                        "repository": f"{self.ecr_repo_url}/cert-manager-cainjector",
                        "tag": "v1.13.2",
                        "pullPolicy": "IfNotPresent",
                    },
                },
                "acemesolver": {
                    "enabled": False,
                },
                "startupapicheck": {
                    "enabled": False,
                },
                "prometheus": {
                    "enabled": False,
                },
            },
        )
