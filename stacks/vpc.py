from constructs import Construct
from aws_cdk import Tags, aws_ec2 as ec2
from lib import constants


def create_vpc(scope: Construct, construct_id: str, **kwargs) -> ec2.Vpc:
    # Create a fully private VPC networking without internet gateways or NAT gateways
    vpc = ec2.Vpc(
        scope,
        construct_id,
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
    Tags.of(vpc).add(
        "Name", f"{constants.STACK_PREFIX}-private-vpc-{constants.STACK_AFFIX}"
    )

    # tag all subnets
    selection = vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED)

    for index, subnet in enumerate(selection.subnets, start=1):
        Tags.of(subnet).add("Name", f"{constants.STACK_PREFIX}-isolated{index}")
        Tags.of(subnet).add("kubernetes.io/role/internal-elb", "1")

    # Add required VPC endpoints
    for svc, n in [
        [ec2.InterfaceVpcEndpointAwsService.EC2, "EC2"],
        [ec2.InterfaceVpcEndpointAwsService.ECR, "ECR"],
        [ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER, "ECRDOCKER"],
        [ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER, "SECRETSMANAGER"],
        [ec2.InterfaceVpcEndpointAwsService.STS, "STS"],
        [ec2.InterfaceVpcEndpointAwsService.CLOUDFORMATION, "CLOUDFORMATION"],
        [ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH, "CLOUDWATCH"],
        [ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS, "CLOUDWATCHLOGS"],
        [ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_EVENTS, "CLOUDWATCHEVENTS"],
        [ec2.InterfaceVpcEndpointAwsService.ELASTIC_FILESYSTEM, "ELASTICFILESYSTEM"],
        [ec2.InterfaceVpcEndpointAwsService.LAMBDA_, "LAMBDA"],
        [ec2.InterfaceVpcEndpointAwsService.STEP_FUNCTIONS, "STEPFUNCTIONS"],
        [ec2.InterfaceVpcEndpointAwsService.STEP_FUNCTIONS_SYNC, "STEPFUNCTIONSSYNC"],
        [
            ec2.InterfaceVpcEndpointAwsService.ELASTIC_LOAD_BALANCING,
            "ELASTICLOADBALANCING",
        ],
        [ec2.InterfaceVpcEndpointAwsService.SSM, "SSM"],
        [ec2.InterfaceVpcEndpointAwsService.EKS, "EKS"],
        [ec2.InterfaceVpcEndpointAwsService.RDS, "RDS"],
        [
            ec2.InterfaceVpcEndpointAwsService.PRIVATE_CERTIFICATE_AUTHORITY,
            "PRIVATECERTIFICATEAUTHORITY",
        ],
        [ec2.InterfaceVpcEndpointAwsService.KMS, "KMS"],
    ]:
        vpc.add_interface_endpoint(
            f"{n}InterfaceEndpoint",
            service=svc,
            private_dns_enabled=True,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
        )

    return vpc
