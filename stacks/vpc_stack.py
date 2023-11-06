from constructs import Construct
from aws_cdk import Stack, Tags, CfnOutput
from aws_cdk import aws_ec2 as ec2
import constants
from typing import List


class VpcStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # TODO: allow a customer provided VPC ID to be used instead of creating one
        if constants.AWS_EXISTING_VPC:
            self.vpc = ec2.Vpc.from_lookup(
                self, "VPC", vpc_id=constants.AWS_VPC_ID, is_default=False
            )
            self.subnets = constants.AWS_PRIVATE_SUBNET_IDS
            return
        else:
            # Create a fully private VPC networking without internet gateways or NAT gateways
            self.vpc = ec2.Vpc(
                self,
                "VPC",
                vpc_name=f"{constants.STACK_PREFIX}-private-vpc",
                ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
                max_azs=4,  # Default is all AZs in the region
                nat_gateways=0,
                create_internet_gateway=False,
                restrict_default_security_group=True,
                subnet_configuration=[
                    ec2.SubnetConfiguration(
                        name=f"{constants.STACK_PREFIX}-Isolated",
                        subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                        cidr_mask=19,  # 4 /18s in /16
                    )
                ],
                enable_dns_support=True,
                enable_dns_hostnames=True,
                gateway_endpoints={
                    "S3Endpoint": ec2.GatewayVpcEndpointOptions(
                        service=ec2.GatewayVpcEndpointAwsService.S3
                        # Add only to ISOLATED subnets - not needed since we only have private subnets
                        # subnets=[aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.PRIVATE_ISOLATED)
                    )
                },
            )
            Tags.of(self.vpc).add("Name", f"{constants.STACK_PREFIX}-private-vpc")

            # tag all subnets
            selection = self.vpc.select_subnets(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            )

            for index, subnet in enumerate(selection.subnets, start=1):
                Tags.of(subnet).add("Name", f"{constants.STACK_PREFIX}-isolated{index}")
                Tags.of(subnet).add("kubernetes.io/role/internal-elb", "true")
                Tags.of(subnet).add(
                    f"kubernetes.io/cluster/{constants.STACK_PREFIX}-eks-cluster",
                    "owned",
                )

            # Add required VPC endpoints
            # ALB Interface Endpoint
            self.vpc.add_interface_endpoint(
                "ALBInterfaceEndpoint",
                service=ec2.InterfaceVpcEndpointAwsService.ELASTIC_LOAD_BALANCING,
                private_dns_enabled=True,
                subnets=ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                ),
            )

            # SSM Interface Endpoint
            self.vpc.add_interface_endpoint(
                "SSMInterfaceEndpoint",
                service=ec2.InterfaceVpcEndpointAwsService.SSM,
                private_dns_enabled=True,
                subnets=ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                ),
            )

            # STS Interface Endpoint
            self.vpc.add_interface_endpoint(
                "STSInterfaceEndpoint",
                service=ec2.InterfaceVpcEndpointAwsService.STS,
                private_dns_enabled=True,
                subnets=ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                ),
            )

            # ECR Docker Interface Endpoint
            self.vpc.add_interface_endpoint(
                "EcrDockerEndpoint",
                service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
                private_dns_enabled=True,
                subnets=ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                ),
            )

            # ECR API Interface Endpoint
            self.vpc.add_interface_endpoint(
                "EcrApiEndpoint",
                service=ec2.InterfaceVpcEndpointAwsService.ECR,
                private_dns_enabled=True,
                subnets=ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                ),
            )

            # EKS Interface Endpoints
            self.vpc.add_interface_endpoint(
                "EKSInterfaceEndpoint",
                service=ec2.InterfaceVpcEndpointAwsService.EKS,
                private_dns_enabled=True,
                subnets=ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                ),
            )

            # CloudWatch Logs Interface Endpoints
            self.vpc.add_interface_endpoint(
                "CloudWatchLogsEndpoint",
                service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
                private_dns_enabled=True,
                subnets=ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                ),
            )

            # CloudWatch Events Interface Endpoints
            self.vpc.add_interface_endpoint(
                "CloudWatchEventsEndpoint",
                service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_EVENTS,
                private_dns_enabled=True,
                subnets=ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                ),
            )

            # CfnOutput for VPC ID
            CfnOutput(self, "VpcId", value=self.vpc.vpc_id)
            # CfnOutput for VPC CIDR
            CfnOutput(self, "VpcCidr", value=self.vpc.vpc_cidr_block)
            # CfnOutput for VPC Isolated Subnet IDs
            CfnOutput(
                self,
                "VpcIsolatedSubnetIds",
                value=", ".join([subnet.subnet_id for subnet in selection.subnets]),
            )

    @property
    def get_vpc(self) -> ec2.Vpc:
        return self.vpc

    @property
    def get_subnets(self) -> List[ec2.ISubnet]:
        if constants.AWS_PRIVATE_SUBNET_IDS:
            return constants.AWS_PRIVATE_SUBNET_IDS
        else:
            return [
                subnet.subnet_id
                for subnet in self.vpc.select_subnets(
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                )
            ]
