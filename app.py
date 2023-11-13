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

vpc_id = os.getenv("AWS_VPC_ID")
private_subnet_ids = os.getenv("AWS_PRIVATE_SUBNET_IDS").split(",")
certificate_arn = os.getenv("AWS_CERTIFICATE_ARN", "")
ecr_repo_url = os.getenv("AWS_ECR_REPO_URL")

print(env)

# Create an EKS Stack with Fargate workers
eks_stack = EksStack(
    app,
    "EksStack",
    stack_name=f"{constants.STACK_PREFIX}-eks-stack2",
    vpc_id=vpc_id,
    private_subnet_ids=private_subnet_ids,
    certificate_arn=certificate_arn,
    ecr_repo_url=ecr_repo_url,
    **env,
)

# app.synth()
app.synth(validate_on_synthesis=True, force=True)
