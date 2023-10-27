import os
from aws_cdk import App, Environment
from stacks.base_stack import BaseStack
from lib.eks_stack import EksStack
from lib.vpc_stack import VpcStack
import constants

app = App()

# env = {
#     "env": Environment(
#         account=constants.AWS_ACCOUNT_ID,
#         region=constants.AWS_REGION,
#     )
# }

# base_stack = BaseStack(
#     app,
#     f"{constants.STACK_PREFIX}BaseStack",
#     **env,
# )

# Create a VPC Stack or detect an existing VPC provided by the customer
vpc_stack = VpcStack(
    app, "VpcStack", stack_name=f"{constants.STACK_PREFIX}-Private-VpcStack"
)

# Create an EKS Stack
eks_stack = EksStack(
    app,
    "EksStack",
    stack_name=f"{constants.STACK_PREFIX}-EksStack",
    vpc=vpc_stack.get_vpc,
)

app.synth()
