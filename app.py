from aws_cdk import App, Environment
from stacks.eks_stack import EksStack
import constants
import os


app = App()

env = {
    "env": Environment(
        account=os.getenv("AWS_ACCOUNT", ""),
        region=os.getenv("AWS_REGION", "us-west-2"),
    )
}

# Create an EKS Stack with Fargate workers
eks_stack = EksStack(
    app, "EksStack", stack_name=f"{constants.STACK_PREFIX}-eks-stack", **env
)

app.synth()
# app.synth(validate_on_synthesis=True, force=True)
