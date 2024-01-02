import os
import json
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_eks as eks,
    aws_iam as iam,
    aws_lambda as lambda_,
)
from constructs import Construct


class AlbStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.IVpc,
        ecr_repo_url: str,
        cluster: eks.Cluster,
        kubectl_role_arn: str,
        kubectl_lambda_role: str,
        # open_id_connect_provider_arn: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = vpc
        self.ecr_repo_url = ecr_repo_url
        self.cluster = cluster
        self.kubectl_role_arn = kubectl_role_arn
        self.kubectl_lambda_role = kubectl_lambda_role

        # -------------------------------------------------------------------------------------------------------------
        # Import KubectlProvider and EKS Cluster ----------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        kubectl_provider = eks.KubectlProvider.from_kubectl_provider_attributes(
            self,
            "KubectlProvider",
            function_arn="",
            kubectl_role_arn=self.kubectl_role_arn,
            handler_role=self.kubectl_lambda_role,
        )
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
                "vpcId": self.vpc.vpc_id,
                "logLevel": "debug",
                "defaultTags": {},
                "defaultTargetType": "ip",
            },
        )
        # add_dependency() method is used to add a dependency on the service_account for the helm_chart.
        # This means that the service_account will be created before the helm_chart is deployed.
        add_alb_chart.node.add_dependency(alb_service_account)
