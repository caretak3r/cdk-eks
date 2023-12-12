from typing import Sequence
from constructs import Construct
from aws_cdk import (
    CfnOutput,
    Duration,
    Stack,
    RemovalPolicy,
    Aws,
    Fn,
    Tags,
    aws_s3 as s3,
    aws_ec2 as ec2,
    aws_iam as iam,
)
from lib import constants


class BaseStack(Stack):
    def __init__(
        self, scope: Construct, id: str, vpc_id, private_subnet_ids, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)
        # -------------------------------------------------------------------------------------------------------------
        # CUSTOMER INPUTS ---------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------

        # If vpc_id and private_subnet_ids are provided, we will use those values
        if vpc_id and private_subnet_ids:
            self.vpc_id = vpc_id
            self.private_subnet_ids = private_subnet_ids

            # We get the VPC type from the provided environment variable
            self.vpc = ec2.Vpc.from_lookup(self, "VPC", vpc_id=self.vpc_id)

            # We get the subnets type from the provided environment variable
            # Strip any spaces in private_subnet_ids since it should just be a comma delimited list
            self.private_subnet_ids = [
                subnet.strip() for subnet in self.private_subnet_ids
            ]
            self.subnets = [
                ec2.Subnet.from_subnet_attributes(
                    self, f"Subnet{n}", subnet_id=self.private_subnet_ids[n]
                )
                for n in range(len(self.private_subnet_ids))
            ]
        else:
            # If vpc_id and private_subnet_ids are not provided, we will create a VPC and subnets
            self.create_vpc(self, "VPC")

        # -------------------------------------------------------------------------------------------------------------
        # S3 Bucket ---------------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        # Create an S3 bucket with encryption and a lifecycle policy, a strict bucket policy only allowing access to objects from an IAM role that EKS will use. Bucket must be fully private
        self.bucket = s3.Bucket(
            self,
            "bucket",
            bucket_name=f"{constants.STACK_PREFIX}-bucket",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            lifecycle_rules=[
                s3.LifecycleRule(
                    enabled=True,
                    abort_incomplete_multipart_upload_after=Duration.days(7),
                    expiration=Duration.days(30),
                )
            ],
            removal_policy=RemovalPolicy.DESTROY,
        )
        self.bucket_policy = iam.PolicyStatement(
            actions=["s3:GetObject", "s3:PutObject"],
            resources=[self.bucket.arn_for_objects("*")],
            principals=[
                iam.Role.from_role_arn(
                    self,
                    "Role",
                    f"arn:aws:iam::{Aws.ACCOUNT_ID}:role/{constants.STACK_PREFIX}*",
                )
            ],
        )
        self.bucket.add_to_resource_policy(self.bucket_policy)

        # -------------------------------------------------------------------------------------------------------------
        # CLOUDFRONT OUTPUTS ------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        CfnOutput(self, "bucket_name", value=self.bucket.bucket_name)
        CfnOutput(self, "bucket_arn", value=self.bucket.bucket_arn)
        CfnOutput(self, "Vpc-Id", value=self.vpc.vpc_id)
        # CfnOutput(
        #     self,
        #     "Subnet-Ids",
        #     value=Fn.join(",", [subnet.subnet_id for subnet in self.subnets]),
        # )

    # -------------------------------------------------------------------------------------------------------------
    # Functions ---------------------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------------------------------

    def create_vpc(self, scope: Construct, construct_id: str):
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
            "Name", f"{constants.STACK_PREFIX}-private-vpc-{constants.STACK_AFFIX}"
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

    @property
    def get_bucket(self) -> s3.Bucket:
        return self.bucket

    @property
    def get_vpc_id(self) -> ec2.IVpc:
        return self.vpc

    @property
    def get_subnet_ids(self) -> Sequence[ec2.ISubnet]:
        return self.subnets
