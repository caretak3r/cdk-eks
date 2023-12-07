from aws_cdk import App, Environment, Tags, Stack
from stacks.eks_stack import EksStack
from stacks.vpc_stack import VpcStack
import constants
import os
from dotenv import load_dotenv
from lib.uuid import generate_uuid

# loads environment variables from .env file
load_dotenv()

# initialize app
app = App()

# TODO: these should match what is in the .env file
env = {
    "env": Environment(
        # profile=os.getenv("AWS_PROFILE", "default"),
        account=os.getenv("AWS_ACCOUNT_ID", ""),
        region=os.getenv("AWS_REGION"),
    )
}

vpc_stack = VpcStack(
    app,
    "VpcStack",
    stack_name=f"{constants.STACK_PREFIX}-vpc-stack-{constants.STACK_AFFIX}",
    **env,
)

print(f"stack template file: {vpc_stack.template_file}")

Tags.of(vpc_stack).add("managed_by", "c1-tkp-cdk")
Tags.of(vpc_stack).add("env", f"{constants.STACK_STAGE}")
Tags.of(vpc_stack).add("deployment_id", f"{generate_uuid()}")

# TODO: add tags for uuid
# TODO: add tags for entity tag?

# Create an EKS Stack with Fargate workers
eks_stack = EksStack(
    app,
    "EksStack",
    stack_name=f"{constants.STACK_PREFIX}-eks-stack-{constants.STACK_AFFIX}",
    vpc_id=os.getenv("AWS_VPC_ID"),
    private_subnet_ids=os.getenv("AWS_PRIVATE_SUBNET_IDS").split(","),
    certificate_arn=os.getenv("AWS_CERTIFICATE_ARN"),
    ecr_repo_url=os.getenv("AWS_ECR_REPO_URL"),
    **env,
)

Tags.of(eks_stack).add("managed_by", "c1-tkp-cdk")
Tags.of(eks_stack).add("env", f"{constants.STACK_STAGE}")
Tags.of(eks_stack).add("deployment_id", f"{generate_uuid()}")

# app.synth()
app.synth(validate_on_synthesis=True, force=True)
