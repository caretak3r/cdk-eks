import os
import json
from aws_cdk import (
    Stack,
    NestedStack,
    CfnOutput,
    aws_ec2 as ec2,
    aws_eks as eks,
    aws_iam as iam,
    aws_eks as eks,
)
from constructs import Construct
from lib import kubectl_helper


class AlbStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.IVpc,
        ecr_repo_url: str,
        eks_cluster: eks.ICluster,
        customer_certificate_arn: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Input variables
        self.vpc = vpc
        self.ecr_repo_url = ecr_repo_url
        self.customer_certificate_arn = customer_certificate_arn

        # Import cluster object
        self.cluster = kubectl_helper.import_cluster(self, eks_cluster)

        # -------------------------------------------------------------------------------------------------------------
        # HELM CHART INSTALL: aws-load-balancer-controller ------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        # Install AWS Load Balancer Controller since we can't use the eks.Cluster construct's alb_controller option
        # since it needs the internet to download. We source from ECR private instead.

        # 1. Creates and Service account for our cluster to add a load Balancer
        # alb_service_account = eks.ServiceAccount(
        alb_service_account = self.cluster.add_service_account(
            "ALBServiceAccount",
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
            "AlbHelmChart",
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
                "vpcId": self.vpc.vpc_id,
                "logLevel": "debug",
                "defaultTags": {},
                "defaultTargetType": "ip",
            },
        )
        # add_dependency() method is used to add a dependency on the service_account for the helm_chart.
        # This means that the service_account will be created before the helm_chart is deployed.
        add_alb_chart.node.add_dependency(alb_service_account)

        # -------------------------------------------------------------------------------------------------------------
        # CloudFormation Outputs ---------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
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
