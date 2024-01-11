from aws_cdk import App, Environment, Tags, Stack
from lib import constants
from lib.unique_id import generate_uuid


def tag_stack(stack: Stack) -> None:
    Tags.of(stack).add("managed_by", f"{constants.STACK_MANAGED_BY}")
    Tags.of(stack).add("env", f"{constants.STACK_STAGE}")
    Tags.of(stack).add("deployment_id", f"{generate_uuid()}")
