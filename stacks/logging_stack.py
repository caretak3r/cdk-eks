from aws_cdk import (
    Stack,
    aws_eks as eks,
    aws_iam as iam,
)
from constructs import Construct


class LoggingStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        eks_cluster: eks.FargateCluster,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create IAM Role for Fluent Bit
        fluent_bit_role = iam.Role(
            self,
            "FluentBitRole",
            assumed_by=iam.ServicePrincipal("eks.amazonaws.com"),
            inline_policies={
                "FluentBitPermissions": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                            resources=["*"],
                        )
                    ]
                )
            },
        )

        # Add Fluent Bit to EKS Cluster
        eks_cluster.add_helm_chart(
            "aws-for-fluent-bit",
            chart="aws-for-fluent-bit",
            repository="https://aws.github.io/eks-charts",
            namespace="kube-system",
            values={
                "fullnameOverride": "aws-for-fluent-bit",
                "serviceAccount": {"create": False, "name": "fluent-bit"},
                "cloudWatch": {
                    "region": self.region,
                    "log_group_name": "/aws/containerinsights/eks-fluent-bit/logs",
                    "log_stream_prefix": "fluent-bit",
                    "auto_create_group": True,
                    "role_arn": fluent_bit_role.role_arn,
                },
            },
        )
