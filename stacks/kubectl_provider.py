from aws_cdk import aws_eks as eks
from stacks.eks_stack_mini import EksStack

def get_kubectl_provider():
    eks_stack = EksStack()
    return eks.KubectlProvider.get_or_create(eks_stack, eks_stack.get_cluster)

