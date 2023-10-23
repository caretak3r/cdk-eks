from aws_cdk import core, Stack, Environment
from lib.eks_stack import EksStack
from lib.vpc_stack import VpcStack
import constants

# from lib.cognito_stack import CognitoStack
# from lib.helm_stack import HelmStack

app = core.App()
stack = Stack(app, "EksCdkProjectStack", env=Environment(region=constants.AWS_REGION))

# Create a VPC Stack
vpc_stack = VpcStack(app, "VPCStack")

# Create an EKS Stack
eks_stack = EksStack(app, "EKSStack", vpc=vpc_stack.vpc)

# Create a Cognito Stack
# cognito_stack = CognitoStack(app, "CognitoStack")

# Create an S3 Stack
# s3_stack = S3Stack(app, "S3Stack")

# Create a Helm Stack
# helm_stack = HelmStack(app, "HelmStack", eks_cluster=eks_stack.eks_cluster)

app.synth()
