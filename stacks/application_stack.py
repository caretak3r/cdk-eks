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


class ApplicationStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        ecr_repo_url: str,
        eks_cluster: eks.ICluster,
        customer_certificate_arn: str,
        customer_apex_domain: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        self.ecr_repo_url = ecr_repo_url
        self.customer_certificate_arn = customer_certificate_arn
        self.customer_apex_domain = customer_apex_domain

        # Import cluster object
        self.cluster = kubectl_helper.import_cluster(self, eks_cluster)
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
            release="http-echo",
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
                "fullnameOverride": "http-echo",
                "podLabels": {"type": "app", "app.kubernetes.io/managed-by": "helm"},
                "labels": {
                    "app.kubernetes.io/managed-by": "helm",
                    "app.kubernetes.io/name": "http-echo",
                },
                "ingress": {
                    "enabled": True,
                    "className": "alb",
                    "annotations": {
                        "kubernetes.io/ingress.class": "alb",
                        "alb.ingress.kubernetes.io/scheme": "internal",
                        "alb.ingress.kubernetes.io/target-type": "ip",
                        "alb.ingress.kubernetes.io/listen-ports": '[{"HTTPS": 443}]',
                        "alb.ingress.kubernetes.io/certificate-arn": self.customer_certificate_arn,
                        "cert-manager.io/cluster-issuer": "ca-cluster-issuer",
                        # "alb.ingress.kubernetes.io/load-balancer-name": "",
                        #"alb.ingress.kubernetes.io/healthcheck-path": "/",
                        #"alb.ingress.kubernetes.io/success-codes": "204",
                        
                        # "alb.ingress.kubernetes.io/actions.ssl-redirect": (
                        #     '{"Type": "redirect", "RedirectConfig": {"Protocol": "HTTPS", "Port": "443", "StatusCode": "HTTP_301"}}'
                        # ),
                    },
                    "hosts": [
                        {
                            "host": f"http-echo.{self.customer_apex_domain}",  # Using the customer domain from the certificate name
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
                    "tls": [
                        {
                            "hosts": [f"http-echo.{self.customer_apex_domain}"],
                            "secretName": f"{constants.CA_SECRET_NAME}",
                        }
                    ],
                },
            },
        )
