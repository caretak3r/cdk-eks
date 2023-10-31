from aws_cdk import aws_ec2 as ec2
from aws_cdk import Stack, Duration, Tags
from constructs import Construct


class BastionStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a bastion host in an existing VPC
        vpc = ec2.vpc