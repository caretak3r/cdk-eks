from constructs import Construct
from aws_cdk import (
    CfnOutput,
    Duration,
    Stack,
    RemovalPolicy,
    Aws,
    Fn,
    Tags,
)
from lib import constants


class CertManagerStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
