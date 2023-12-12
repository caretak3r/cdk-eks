from aws_cdk import App, Environment, Tags, Stack
import constants
from lib.uuid import generate_uuid


def tag_stack(stack: Stack) -> None:
    Tags.of(stack).add("managed_by", "c1-tkp-cdk")
    Tags.of(stack).add("env", f"{constants.STACK_STAGE}")
    Tags.of(stack).add("deployment_id", f"{generate_uuid()}")
