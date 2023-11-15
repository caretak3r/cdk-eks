from aws_cdk import App, Environment
from stacks.eks_stack import EksStack
import constants
import os
from dotenv import load_dotenv

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

env_vars = [
    "AWS_VPC_ID",
    "AWS_PRIVATE_SUBNET_IDS",
    "AWS_ECR_REPO_URL"
    # "AWS_CERTIFICATE_ARN",
]

for var in env_vars:
    if not os.getenv(var):
        print(f"{var} is not set.")
        user_input = input(f"Please enter a value for {var}: ")
        if user_input:
            os.environ[var] = user_input
        else:
            print(f"{var} is required. Exiting script.")
            exit(1)

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

# app.synth()
app.synth(validate_on_synthesis=True, force=True)
