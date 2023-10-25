from setuptools import setup, find_packages

setup(
    name="cdk-eks-fargate",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "aws-cdk.core",
        "aws-cdk.aws-eks",
        "aws-cdk.aws-cognito",
        "aws-cdk.aws-ec2",
        "aws-cdk.aws-iam",
        "aws-cdk.aws-ecr-assets",
        "boto3",
        "awscli",
        "pyhelm",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="This is a CDK Python app that supports EKS with Fargate profiles within an existing VPC and network resources, or let the user create a new vpc and dependent network resources, cognito, and deploy helm charts from an ECR repository.",
    license="Apache License Version 2.0",
    keywords="aws cdk eks fargate cognito apigateway helm",
    url="http://github.com/yourname/cdk-eks",
)
