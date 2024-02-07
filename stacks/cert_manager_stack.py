from aws_cdk import (
    Aws,
    CfnOutput,
    Duration,
    Fn,
    RemovalPolicy,
    Stack,
    Tags,
)
from aws_cdk import (
    aws_eks as eks,
)
from aws_cdk import (
    aws_secretsmanager as ssm,
)
from constructs import Construct

from lib import constants, kubectl_helper
from stacks.kms import create_kms_key


class CertManagerStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        ecr_repo_url: str,
        eks_cluster: eks.ICluster,
        customer_certificate_arn: str,
        customer_apex_domain: str,
        customer_managed_cmk: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Input variables
        self.ecr_repo_url = ecr_repo_url
        self.customer_certificate_arn = customer_certificate_arn
        self.customer_apex_domain = customer_apex_domain

        # Import cluster object
        self.cluster = kubectl_helper.import_cluster(self, eks_cluster)

        # -------------------------------------------------------------------------------------------------------------
        # KMS/CMK Key Creation ----------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        # If the customer_managed_cmk is provided, we will use that value
        # If the customer_managed_cmk is not provided, we will create a CMK key using stacks/kms.py construct with
        # predefined configurations.
        if not customer_managed_cmk:
            self.customer_managed_cmk = create_kms_key(
                self,
                "SecretsManagerCmk",
                self.region,
                self.account,
                enable_key_rotation=True,
            )
        # -------------------------------------------------------------------------------------------------------------
        # HELM CHART INSTALL: cert-manager ----------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        # Install cert-manager helm chart from ECR private
        # 1. Generate a secret for the customer certificate and store it in AWS Secrets Manager
        ca_certificate_secret = ssm.Secret(
            self,
            "CACertificateSecret",
            secret_name=f"{constants.CA_SECRET_NAME}",
            generate_secret_string=ssm.SecretStringGenerator(
                secret_string_template='{"ca_certificate": "%s"}',
                generate_string_key="certificate",
                password_length=4096,
                exclude_characters='"@\\\/',  # TODO: check if this is correct for a certificate secret
                exclude_punctuation=True,
            ),
            removal_policy=constants.CA_SECRET_REMOVAL_POLICY,
            description="Secret for the cert-manager CA certificate",
        )

        # 2. Creates a Helm chart for the cert-manager
        add_cert_manager_chart = self.cluster.add_helm_chart(
            "cert-manager",
            repository=f"oci://{self.ecr_repo_url}/cert-manager-helm-chart",
            chart="cert-manager-helm-chart",
            version="v1.13.2",
            release="cert-manager",
            create_namespace=True,
            namespace="cert-manager",
            values={
                "leaderElection": {"namespace": "cert-manager"},
                "logLevel": 5,
                "installCRDs": True,
                "fullnameOverride": "cert-manager",
                "replicaCount": 1,
                "image": {
                    "repository": f"{self.ecr_repo_url}/cert-manager-controller",
                    "tag": "v1.13.2",
                    "pullPolicy": "IfNotPresent",
                },
                "webhook": {
                    "securePort": 10260,  # Fargate requirement
                    "replicaCount": 1,
                    "image": {
                        "repository": f"{self.ecr_repo_url}/cert-manager-webhook",
                        "tag": "v1.13.2",
                        "pullPolicy": "IfNotPresent",
                    },
                },
                "cainjector": {
                    "enabled": True,
                    "replicaCount": 1,
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
            wait=True,
        )
        # add_cert_manager_chart.node.add_dependency(ca_certificate_secret)

        # # # 3. Create self signed cluster issuer (1)
        self_signed_cluster_issuer = self.cluster.add_manifest(
            "SelfSignedClusterIssuer",
            {
                "apiVersion": "cert-manager.io/v1",
                "kind": "ClusterIssuer",
                "metadata": {
                    "name": "selfsigned-cluster-issuer",
                },
                "spec": {
                    "selfSigned": {},
                },
            },
        )
        # # self_signed_cluster_issuer.node.add_dependency(ca_certificate_secret)

        # # # 4. Create CA Certificate using the secret (2)
        # ca_certificate = self.cluster.add_manifest(
        #     "CACertificate",
        #     {
        #         "apiVersion": "cert-manager.io/v1",
        #         "kind": "Certificate",
        #         "metadata": {"name": "selfsigned-ca", "namespace": "cert-manager"},
        #         "spec": {
        #             "labels": {"app.kubernetes.io/managed-by:": "helm", "ops": "cert"},
        #             "secretName": ca_certificate_secret.secret_name,
        #             "privateKey": {"algorithm": "ECDSA", "size": 256},
        #             # "commonName": f"${self.customer_apex_domain}",
        #             "commonName": "selfsigned-ca",
        #             "subject": {
        #                 "organizations": [
        #                     f"{constants.STACK_PREFIX}"
        #                 ],  # TODO: change this to something that makes sense
        #                 "countries": ["US"],
        #                 "organizationalUnits": [
        #                     f"{constants.STACK_PREFIX}Engineering"
        #                 ],  # TODO: change this to something that makes sense
        #             },
        #             "isCA": True,
        #             "issuerRef": {
        #                 "name": "selfsigned-cluster-issuer",
        #                 "kind": "ClusterIssuer",
        #                 "group": "cert-manager.io",
        #             },
        #         },
        #     },
        # )
        # ca_certificate.node.add_dependency(ca_certificate_secret)
        # # ca_certificate.node.add_dependency(add_cert_manager_chart)

        # # # 5. Create cluster issuer
        # cluster_issuer = self.cluster.add_manifest(
        #     "ClusterIssuer",
        #     {
        #         "apiVersion": "cert-manager.io/v1",
        #         "kind": "ClusterIssuer",
        #         "metadata": {
        #             "name": "ca-cluster-issuer",
        #             "app.kubernetes.io/managed-by:": "helm",
        #             "ops": "cert",
        #         },
        #         "spec": {
        #             "ca": {
        #                 "secretName": ca_certificate_secret.secret_name,
        #             },
        #         },
        #     },
        # )
        # cluster_issuer.node.add_dependency(ca_certificate_secret)
        # # cluster_issuer.node.add_dependency(add_cert_manager_chart)
