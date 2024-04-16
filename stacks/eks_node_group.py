from typing import Sequence, List
from lib import constants
from aws_cdk import (
    CfnOutput,
    Fn,
    Stack,
    Tags,
    aws_eks as eks,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_lambda as lambda_,
)
from aws_cdk.lambda_layer_kubectl_v28 import KubectlV28Layer
from constructs import Construct
from stacks.kms import create_kms_key

class EksStack_NodeGroup(Stack):
    cluster: eks.Cluster
    
    def __init__(
        self,
        scope: Construct,
        id: str,
        vpc: ec2.IVpc,
        subnets: Sequence[ec2.ISubnet],
        customer_managed_cmk: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # Create KMS Key if one isn't provided
        if not customer_managed_cmk:
            self.customer_managed_cmk = create_kms_key(
                self,
                "EksCmk",
                self.region,
                self.account,
                enable_key_rotation=True
            )
        
        # Create Kubectl Layer
        kubectl_layer = KubectlV28Layer(self, "KubectlV28Layer")

        # Create Standalone EKS Cluster 
        self.cluster = eks.Cluster(
            self,
            "EKSCluster",
            cluster_name=f"{constants.STACK_PREFIX}-eks-node-group-cluster-{constants.STACK_SUFFIX}",
            cluster_logging=[
                eks.ClusterLoggingTypes.API,
                eks.ClusterLoggingTypes.AUDIT,
                eks.ClusterLoggingTypes.AUTHENTICATOR,
                eks.ClusterLoggingTypes.CONTROLLER_MANAGER,
                eks.ClusterLoggingTypes.SCHEDULER,
            ],
            core_dns_compute_type=eks.CoreDnsComputeType.EC2,
            endpoint_access=eks.EndpointAccess.PUBLIC_AND_PRIVATE,
            kubectl_layer=kubectl_layer,
            output_cluster_name=True,
            output_config_command=True,
            output_masters_role_arn=True,
            place_cluster_handler_in_vpc=True,
            cluster_handler_environment={"AWS_STS_REGIONAL_ENDPOINTS": "regional"},
            kubectl_environment={"AWS_STS_REGIONAL_ENDPOINTS": "regional"},
            secrets_encryption_key=self.customer_managed_cmk,
            version=eks.KubernetesVersion.V1_28,
            default_capacity=3,
            default_capacity_instance=ec2.InstanceType.of(ec2.InstanceClass.M5, ec2.InstanceSize.LARGE),
            vpc=vpc,
            vpc_subnets=[ec2.SubnetSelection(subnets=subnets)],
        )
        Tags.of(self.cluster).add(
            "Name",
            f"{constants.STACK_PREFIX}-eks-cluster-{constants.STACK_SUFFIX}",
        )

        self.add_to_masters_role()

        # -------------------------------------------------------------------------------------------------------------
        # CLOUDFRONT OUTPUTS ------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        CfnOutput(self, "AWS REGION", value=self.region)
        CfnOutput(self, "AWS ACCOUNT ID", value=self.account)
        CfnOutput(
            self,
            "ClusterName",
            value=self.cluster.cluster_name,
            description="EKS Node Group cluster name",
        )
        CfnOutput(
            self,
            "ClusterArn",
            value=self.cluster.cluster_arn,
            description="EKS Node Group cluster ARN",
        )
        CfnOutput(
            self,
            "ClusterEndpoint",
            value=self.cluster.cluster_endpoint,
            description="EKS Node Group cluster endpoint",
        )
        CfnOutput(self, "Vpc-Id", value=vpc.vpc_id, description="VPC ID")
        CfnOutput(
            self,
            "Subnet-Ids",
            value=Fn.join(",", [subnet.subnet_id for subnet in subnets]),
            description="Subnet IDs",
        )
        CfnOutput(
            self,
            "CustomerManagedCmkArn",
            value=self.customer_managed_cmk.key_arn,
            description="Customer Managed CMK for EKS envelope encryption",
        )
        CfnOutput(
            self,
            "SecurityGroupId",
            value=self.cluster.cluster_security_group_id,
            description="Security Group ID",
        )
        CfnOutput(
            self,
            "ClusterMastersRoleArn",
            value=self.cluster.kubectl_role.role_arn,
            description="Cluster Masters Role ARN",
        )

    # -------------------------------------------------------------------------------------------------------------
    # Property and Other Functions --------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------------------------------

    @property
    def get_vpc(self) -> ec2.IVpc:
        return self.cluster.vpc
    
    @property
    def get_subnets(self) -> Sequence[ec2.ISubnet]:
        return self.cluster.vpc.private_subnets

    @property
    def get_cluster(self) -> eks.ICluster:
        return self.cluster

    @property
    def get_cluster_name(self) -> str:
        return self.cluster.cluster_name

    @property
    def get_cluster_endpoint(self) -> str:
        return self.cluster.cluster_endpoint

    @property
    def get_kubectl_role_arn(self) -> str:
        return self.cluster.kubectl_role.role_arn

    @property
    def get_kubectl_lambda_role(self) -> str:
        return self.cluster.kubectl_lambda_role.role_arn

    @property
    def get_kubectl_layer(self) -> lambda_.ILayerVersion:
        return self.cluster.kubectl_layer

    @property
    def get_open_id_connect_provider_arn(self) -> str:
        return self.cluster.open_id_connect_provider.open_id_connect_provider_arn

    def _is_valid_arn_list(self, arn_list: List[str]) -> bool:
        if not arn_list or arn_list == [""]:
            return False
        if len(arn_list) > 0 and arn_list[0].startswith("arn"):
            return True
        return False

    def add_to_masters_role(self) -> None:
        # IAM: Add IAM roles from constants to the `system:masters` group
        # TODO: how will this work in a customer environment? Do we assign the operator's role to the cluster?
        if self._is_valid_arn_list(constants.AUTHORIZED_ROLE_LIST):
            for role in constants.AUTHORIZED_ROLE_LIST:
                auth_role = iam.Role.from_role_arn(
                    self, f"ImportedIAMRole{role.split('/')[-1]}", role
                )
                # self.cluster.aws_auth.add_role_mapping(auth_role, groups=["system:masters"])
                self.cluster.aws_auth.add_masters_role(auth_role)

                self.cluster.add_manifest(
                    f"AdminRoleManifest{role.split('/')[-1]}",
                    {
                        "apiVersion": "rbac.authorization.k8s.io/v1",
                        "kind": "ClusterRoleBinding",
                        "metadata": {"name": "admin-role-binding"},
                        "roleRef": {
                            "apiGroup": "rbac.authorization.k8s.io",
                            "kind": "ClusterRole",
                            "name": "cluster-admin",
                        },
                        "subjects": [
                            {
                                "kind": "ServiceAccount",
                                "name": auth_role.role_name,
                                "namespace": "kube-system",
                            }
                        ],
                    },
                )
        else:
            return
        

    