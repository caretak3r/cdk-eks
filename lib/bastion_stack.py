from aws_cdk import aws_ec2 as ec2
from aws_cdk import Stack, CfnOutput
from constructs import Construct
import constants


class BastionStack(Stack):
    def __init__(
        self,
        scope: Construct,
        vpc: ec2.Vpc,
        subnets: ec2.SubnetSelection,
        id: str,
        **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        host_bastion = ec2.BastionHostLinux(
            self, "BastionHost", vpc=vpc, subnet_selection=subnets
        )

        for ip in constants.BASTION_WHITELIST_IP:
            host_bastion.allow_ssh_access_from(ec2.Peer.ipv4(ip))

        # use amazon linux as OS
        amzn_linux = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE,
        )
        # secure group
        my_security_group = ec2.SecurityGroup(
            self,
            "SecurityGroup",
            vpc=vpc,
            description="SecurityGroup from CDK",
            security_group_name="CDK SecurityGroup",
            allow_all_outbound=True,
        )
        my_security_group.add_ingress_rule(
            ec2.Peer.ipv4("172.31.0.0/16"),
            ec2.Port.tcp(22),
            "allow ssh access from the VPC",
        )

        # create a VPC peering to another VPC in the same account and update route table
        vpc_peering = ec2.CfnVPCPeeringConnection(
            self,
            "VPCPeering",
            vpc_id=vpc.vpc_id,
            peer_vpc_id=constants.AWS_VPC_ID,
            peer_region=constants.AWS_REGION,
            peer_owner_id=constants.AWS_ACCOUNT_ID,
        )

        update_route_table = ec2.CfnRoute(
            self,
            "RouteTable",
            route_table_id=constants.BASTION_ROUTE_TABLE_ID,
            destination_cidr_block="10.0.0.0/16",
            vpc_peering_connection_id=vpc_peering.ref,
        )

        # output information after deploy
        output = CfnOutput(
            self,
            "BastionHost_information",
            value=host_bastion.instance_public_ip,
            description="BastionHost's Public IP",
        )
