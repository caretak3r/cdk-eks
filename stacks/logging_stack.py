from constructs import Construct
from aws_cdk import (
    aws_eks as eks,
    aws_iam as iam,
    CfnOutput,
    Duration,
    Stack,
    RemovalPolicy,
    Aws,
    Fn,
    Tags,
)
from lib import constants
from lib import kubectl_helper


class LoggingStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        eks_cluster: eks.ICluster,
        pod_execution_role: iam.IRole,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # Import cluster object
        self.cluster = kubectl_helper.import_cluster(self, eks_cluster)

        logging_namespace = self.cluster.add_manifest(
            "aws-observertility",
            {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {
                    "name": "aws-observability",
                    "labels": {
                        "name": "aws-observability",
                        "aws-observability": "enabled",
                    },
                },
            },
        )

        fluent_bit_policy_statement = iam.PolicyStatement(
            actions=[
                "logs:CreateLogStream",
                "logs:CreateLogGroup",
                "logs:DescribeLogStreams",
                "logs:PutLogEvents",
                "logs:PutRetentionPolicy",
            ],
            resources=["*"],
            effect=iam.Effect.ALLOW,
        )

        fluent_bit_policy = iam.Policy(
            self,
            "FluentBitPolicy",
            policy_name=f"{constants.STACK_PREFIX}FluentBitPolicy{constants.STACK_SUFFIX}",
            statements=[fluent_bit_policy_statement],
        )

        pod_execution_role.attach_inline_policy(fluent_bit_policy)

        # Create service account for FluentBit
        fluent_bit_service_account = self.cluster.add_service_account(
            "FluentBitServiceAccount",
            name="fluent-bit",
            namespace="aws-observability",
        )

        fluent_bit_service_account.add_to_principal_policy(fluent_bit_policy_statement)

        # Deploy FluentBit manifest
        fluent_bit_manifest = self.cluster.add_manifest(
            "FluentBitManifest",
            {
                "kind": "ConfigMap",
                "apiVersion": "v1",
                "metadata": {"name": "aws-logging", "namespace": "aws-observability"},
                "data": {
                    "flb_log_cw": "false",
                    "filters.conf": "[FILTER]\n     Name parser\n     Match *\n     Key_name log\n     Parser crio\n[FILTER]\n     Name kubernetes\n     Match kube.*\n     Merge_Log On\n     Keep_Log Off\n     Buffer_Size 0\n     Kube_Meta_Cache_TTL 300s\n",
                    "output.conf": f"[OUTPUT]\n     Name cloudwatch_logs\n     Match kube.*\n     region {self.region}\n    log_group_name cdk-cloudwatch-logs\n     log_stream_prefix {self.cluster.cluster_name}\n     log_retention_days 60\n     auto_create_group true\n[OUTPUT]\n     Name cloudwatch_logs\n     Match *alb*\n     region {self.region}\n     log_group_name alb-cdk-cloudwatch-logs\n     log_stream_prefix {self.cluster.cluster_name}\n     log_retention_days 60\n     auto_create_group true\n[OUTPUT]\n     Name cloudwatch_logs\n     Match *cert*\n     region {self.region}\n     log_group_name alb-cdk-cloudwatch-logs\n     log_stream_prefix {self.cluster.cluster_name}\n     log_retention_days 60\n     auto_create_group true\n",
                    "parsers.conf": "[PARSER]\n     Name crio\n     Format Regex\n     Regex ^(?<time>[^ ]+) (?<stream>stdout|stderr) (?<logtag>P|F) (?<log>.*)$\n   Time_Key time\n     Time_Format %Y-%m-%dT%H:%M:%S.%L%z\n     Time_Keep On\n     Decode_Field_As escaped_utf8 log\n     Decode_Field_As json log\n",
                },
            },
        )

        fluent_bit_manifest.node.add_dependency(logging_namespace)
        fluent_bit_manifest.node.add_dependency(fluent_bit_service_account)
