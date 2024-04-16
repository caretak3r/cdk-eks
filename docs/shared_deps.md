# Plan

Below is a plan for a Python AWS CDK project, which supports EKS with Fargate profiles. The project can work with existing VPC and network resources or it can generate a new VPC and dependent network resources. The project will also include Cognito, API Gateway and will deploy helm charts from an ECR repository. 

The project will be structured into several Python files, each handling a specific part of the stack.

## `app.py`
This is the entry point of the CDK application. It will define the application and the stacks.

Exports: `app` - the CDK application instance

## `vpc_stack.py`
This file will define a VPC Stack, which will either create a new VPC or use an existing one based on user input.

Exports: `VpcStack` - the CDK stack for VPC

## `eks_stack.py`
This file will define an EKS Stack. It will create an EKS cluster with Fargate profiles within the VPC defined in `vpc_stack.py`.

Exports: `EksStack` - the CDK stack for EKS

## `cognito_stack.py`
This file will define a Cognito Stack, which will create a new Cognito User Pool.

Exports: `CognitoStack` - the CDK stack for Cognito

## `api_gateway_stack.py`
This file will define an API Gateway Stack, which will create a new API Gateway and link it to the services in the EKS cluster.

Exports: `ApiGatewayStack` - the CDK stack for API Gateway

## `helm_stack.py`
This file will define a Helm Stack, which will deploy Helm charts from an ECR repository to the EKS cluster.

Exports: `HelmStack` - the CDK stack for Helm deployment

## `cdk.json`
This file will contain the CDK configuration, including the command to run the application.

## `requirements.txt`
This file will list all the Python dependencies for the CDK application.

## `setup.py`
This file will define the Python package, including metadata and dependencies.

The stacks will be connected using CDK's built-in methods for passing resources between stacks. For example, the VPC created in `vpc_stack.py` will be passed to `eks_stack.py` to create the EKS cluster in the same VPC.