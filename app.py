from aws_cdk import App, Environment, Tags
from stacks.eks_stack import EksStack
from stacks.vpc_stack import VpcStack
import constants
import os
from dotenv import load_dotenv
import uuid
import hashlib

# loads environment variables from .env file
load_dotenv()


def generate_uuid():
    try:
        uuid_value = uuid.uuid4()
        assert uuid.UUID(str(uuid_value), version=4)
    except ValueError:
        uuid_value = hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()
    return uuid_value


print(f"Unique ID for this deployment run: {generate_uuid()}")

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

Tags.of(vpc_stack).add("managed_by", "platform-cdk")
Tags.of(vpc_stack).add("env", f"{constants.STACK_STAGE}")

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

Tags.of(eks_stack).add("managed_by", "platform-cdk")
Tags.of(eks_stack).add("env", f"{constants.STACK_STAGE}")

# app.synth()
app.synth(validate_on_synthesis=True, force=True)
