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
    aws_secretsmanager as ssm,
)
from lib import constants
from lib import kubectl_helper


class CertManagerStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        ecr_repo_url: str,
        eks_cluster: eks.ICluster,
        customer_certificate_arn: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.ecr_repo_url = ecr_repo_url
        self.customer_certificate_arn = customer_certificate_arn

        # Import cluster object
        self.cluster = kubectl_helper.import_cluster(self, eks_cluster)

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
                "replicaCount": 3,
                "image": {
                    "repository": f"{self.ecr_repo_url}/cert-manager-controller",
                    "tag": "v1.13.2",
                    "pullPolicy": "IfNotPresent",
                },
                "webhook": {
                    "securePort": 10260,  # Fargate requirement
                    "replicaCount": 3,
                    "image": {
                        "repository": f"{self.ecr_repo_url}/cert-manager-webhook",
                        "tag": "v1.13.2",
                        "pullPolicy": "IfNotPresent",
                    },
                },
                "cainjector": {
                    "enabled": True,
                    "replicaCount": 3,
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

        # 2. Create self signed cluster issuer
        self_signed_cluster_issuer = self.cluster.add_manifest(
            "SelfSignedClusterIssuer",
            {
                "apiVersion": "cert-manager.io/v1",
                "kind": "ClusterIssuer",
                "metadata": {"name": "selfsigned-cluster-issuer"},
                "spec": {
                    "selfSigned": {},
                },
            },
        )

        # 3. Generate a secret for the customer certificate and store it in AWS Secrets Manager
        ca_certificate_secret = ssm.Secret(
            self,
            "CACertificateSecret",
            generate_secret_string=ssm.SecretStringGenerator(
                secret_string_template='{"ca_certificate": "%s"}',
                generate_string_key="certificate",
                password_length=4096,
                exclude_punctuation=True,
            ),
        )

        # 4. Create CA Certificate using the secret
        ca_certificate = self.cluster.add_manifest(
            "CACertificate",
            {
                "apiVersion": "cert-manager.io/v1",
                "kind": "Certificate",
                "metadata": {"name": "ca-certificate", "namespace": "cert-manager"},
                "spec": {
                    "secretName": ca_certificate_secret.secret_name,
                    "privateKey": {"algorithm": "ECDSA", "size": 256},
                    "commonName": "tkp.internal",
                    "subject": {
                        "organizations": ["tkp"],
                        "countries": ["US"],
                        "organizationalUnits": ["tkp"],
                    },
                    "isCA": True,
                    "issuerRef": {
                        "name": "selfsigned-cluster-issuer",
                        "kind": "ClusterIssuer",
                        "group": "cert-manager.io",
                    },
                },
            },
        )

        # 5. Create cluster issuer
        cluster_issuer = self.cluster.add_manifest(
            "ClusterIssuer",
            {
                "apiVersion": "cert-manager.io/v1",
                "kind": "ClusterIssuer",
                "metadata": {"name": "ca-cluster-issuer"},
                "spec": {
                    "ca": {
                        "secretName": ca_certificate_secret.secret_name,
                    },
                },
            },
        )

        # 6.  Create Ingress in a different namespace that should use the new cluster issuer
        ingress = self.cluster.add_manifest(
            "Ingress",
            {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "Ingress",
                "metadata": {"name": "test-ingress", "namespace": "default"},
                "spec": {
                    "tls": [
                        {
                            "hosts": ["tkp.internal"],
                            "secretName": "test-ingress-cert",
                        }
                    ],
                    "rules": [
                        {
                            "host": "tkp.internal",
                            "http": {
                                "paths": [
                                    {
                                        "path": "/",
                                        "pathType": "Prefix",
                                        "backend": {
                                            "service": {
                                                "name": "test-service",
                                                "port": {"number": 80},
                                            }
                                        },
                                    }
                                ]
                            },
                        }
                    ],
                },
            },
        )
