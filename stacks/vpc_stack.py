from constructs import Construct
from aws_cdk import Stack, Tags, CfnOutput
from aws_cdk import aws_ec2 as ec2
from lib import constants


class VpcStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

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
        Tags.of(self.vpc).add(
            "Name", f"{constants.STACK_PREFIX}-private-vpc-{constants.STACK_SUFFIX}"
        )

        # tag all subnets
        selection = self.vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED)

        for index, subnet in enumerate(selection.subnets, start=1):
            Tags.of(subnet).add("Name", f"{constants.STACK_PREFIX}-isolated{index}")
            Tags.of(subnet).add("kubernetes.io/role/internal-elb", "1")
            # This tag was only used by Amazon EKS. You can remove the tag without impacting your services. It's not used with clusters that are version 1.15 or later.
            # Tags.of(subnet).add(
            #     f"kubernetes.io/cluster/{constants.STACK_PREFIX}-eks-cluster",
            #     "owned",
            # )

        # Add required VPC endpoints

        # Lambda Interface Endpoint
        self.vpc.add_interface_endpoint(
            "EFSInterfaceEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.ELASTIC_FILESYSTEM,
            private_dns_enabled=True,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
        )

        # Lambda Interface Endpoint
        self.vpc.add_interface_endpoint(
            "LambdaInterfaceEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.LAMBDA_,
            private_dns_enabled=True,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
        )

        # Step Functions Sync Interface Endpoint
        self.vpc.add_interface_endpoint(
            "StatesInterfaceEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.STEP_FUNCTIONS,
            private_dns_enabled=True,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
        )
        # Step Functions Sync Interface Endpoint
        self.vpc.add_interface_endpoint(
            "StatesSyncInterfaceEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.STEP_FUNCTIONS_SYNC,
            private_dns_enabled=True,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
        )

        # EC2 Interface Endpoint
        self.vpc.add_interface_endpoint(
            "EC2InterfaceEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.EC2,
            private_dns_enabled=True,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
        )

        # ALB Interface Endpoint
        self.vpc.add_interface_endpoint(
            "ALBInterfaceEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.ELASTIC_LOAD_BALANCING,
            private_dns_enabled=True,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
        )

        # SSM Interface Endpoint
        self.vpc.add_interface_endpoint(
            "SSMInterfaceEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.SSM,
            private_dns_enabled=True,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
        )

        # STS Interface Endpoint
        self.vpc.add_interface_endpoint(
            "STSInterfaceEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.STS,
            private_dns_enabled=True,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
        )

        # ECR Docker Interface Endpoint
        self.vpc.add_interface_endpoint(
            "EcrDockerEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
            private_dns_enabled=True,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
        )

        # ECR API Interface Endpoint
        self.vpc.add_interface_endpoint(
            "EcrApiEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.ECR,
            private_dns_enabled=True,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
        )

        # EKS Interface Endpoints
        self.vpc.add_interface_endpoint(
            "EKSInterfaceEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.EKS,
            private_dns_enabled=True,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
        )

        # CloudWatch Interface Endpoints
        self.vpc.add_interface_endpoint(
            "CloudWatchEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH,
            private_dns_enabled=True,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
        )

        # CloudWatch Logs Interface Endpoints
        self.vpc.add_interface_endpoint(
            "CloudWatchLogsEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
            private_dns_enabled=True,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
        )

        # CloudWatch Events Interface Endpoints
        self.vpc.add_interface_endpoint(
            "CloudWatchEventsEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_EVENTS,
            private_dns_enabled=True,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
        )

        # CloudFormation Interface Endpoints
        self.vpc.add_interface_endpoint(
            "CloudFormationEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDFORMATION,
            private_dns_enabled=True,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
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
