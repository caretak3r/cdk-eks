from constructs import Construct
from aws_cdk import Stack, Tags
from aws_cdk import aws_ec2 as ec2
import constants


class VpcStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # TODO: allow a customer provided VPC to be used instead of creating one
        if constants.AWS_EXISTING_VPC:
            self.vpc = ec2.Vpc.from_lookup(
                self, "VPC", vpc_id=constants.AWS_VPC_ID, is_default=False
            )
            return
        else:
            # Create a fully private VPC networking without internet gateways or NAT gateways
            self.vpc = ec2.Vpc(
                self,
                "VPC",
                vpc_name=f"{constants.STACK_PREFIX}VPC",
                cidr="10.0.0.0/16",
                max_azs=3,  # Default is all AZs in the region
                nat_gateways=0,
                create_internet_gateway=False,
                restrict_default_security_group=True,
                subnet_configuration=[
                    ec2.SubnetConfiguration(
                        name=f"{constants.STACK_PREFIX}IsolatedSubnet",
                        subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                        cidr_mask=18,  # 4 /18s in /16
                    )
                ],
                enable_dns_support=True,
                enable_dns_hostnames=True,
                gateway_endpoints={
                    "S3": ec2.GatewayVpcEndpointOptions(
                        service=ec2.GatewayVpcEndpointAwsService.S3
                    )
                },
            )
            Tags.of(self.vpc).add("Name", f"{constants.STACK_PREFIX}VPC")

            # Add required VPC endpoints
            # TODO: add endpoint policies
            # SSM Interface Endpoint
            self.vpc.add_interface_endpoint(
                "SSMInterfaceEndpoint", service=ec2.InterfaceVpcEndpointAwsService.SSM
            )

            # STS Interface Endpoint
            self.vpc.add_interface_endpoint(
                "STSInterfaceEndpoint", service=ec2.InterfaceVpcEndpointAwsService.STS
            )

            # ECR Interface Endpoint
            self.vpc.add_interface_endpoint(
                "EcrDockerEndpoint",
                service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
            )

            # EKS Interface Endpoints
            self.vpc.add_interface_endpoint(
                "EKSInterfaceEndpoint", service=ec2.InterfaceVpcEndpointAwsService.EKS
            )

            # # CloudWatch Interface Endpoints
            # self.vpc.add_interface_endpoint(
            #     "CloudWatchLogsEndpoint",
            #     service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
            # )
            # self.vpc.add_interface_endpoint(
            #     "CloudWatchEventsEndpoint",
            #     service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_EVENTS,
            # )

    @property
    def get_vpc(self) -> ec2.Vpc:
        return self.vpc
