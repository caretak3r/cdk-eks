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
from lib import kubectl_helper


class NetworkPolicyStack(Stack):
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
