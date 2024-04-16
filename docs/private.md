# Private

Various issues building a CDK EKS Fargate enabled cluster: 

1. Lambdas cannot access the EKS cluster service endpoints:
    Error: `CloudFormation did not receive a response from your Custom Resource.`
    - [ ] Previously this was due to a lack of an EKS VPC endpoint, but one exists now and is implemented. 
    - [ ] Enable the use of STS VPC endpoint to keep permission requests private. 

2. Limitation around creating clusters in isolated VPCs
    Error: `CloudFormation did not receive a response from your Custom Resource.`
    REF: https://github.com/aws/aws-cdk/issues/12171

3. 

