from aws_cdk import App, Environment
from stacks.base_stack import BaseStack
from stacks.eks_stack import EksStack
from stacks.vpc_stack import VpcStack
from stacks.rds_stack import RdsStack
import constants

app = App()

env = {
    "env": Environment(
        account=constants.AWS_ACCOUNT_ID,
        region=constants.AWS_REGION,
    )
}

# create an ecr repo with encryption, image scanning, and a lifecycle policy, and replication policy to c1 account
base_stack = BaseStack(
    app,
    "BaseStack",
    stack_name=f"{constants.STACK_PREFIX}-base-stack",
    ecr_repo=constants.AWS_ECR_REPOSITORY_NAME,
    **env,
)

# Create a VPC Stack or detect an existing VPC provided by the customer
vpc_stack = VpcStack(
    app, "VpcStack", stack_name=f"{constants.STACK_PREFIX}-private-vpc-stack"
)

# Create an EKS Stack with Fargate workers
eks_stack = EksStack(
    app,
    "EksStack",
    stack_name=f"{constants.STACK_PREFIX}-eks-stack",
    vpc=vpc_stack.get_vpc,
)

rds_stack = RdsStack(
    app,
    "RdsStack",
    stack_name=f"{constants.STACK_PREFIX}-rds-stack",
    vpc=vpc_stack.get_vpc,
)

app.synth(
    validate_on_synthesis=True,
    force=True,
)
