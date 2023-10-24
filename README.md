# eks-cdk-project

This project uses python AWS CDK to deploy a private VPC and networking resources, an EKS cluster with Fargate enabled profiles, a Cognito pool, S3 buckets, Route53 configurations, and deploys helm charts to the resulting cluster.

---

## Bootstrap

Use bootstrap to provision a new ECR plus configurations.


## Deploy

---

## Todo

1. https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/configure-mutual-tls-authentication-for-applications-running-on-amazon-eks.html

2. https://eksctl.io/usage/kms-encryption/

3. Use an existing VPC from the customer if passed in as a parameter input during synthesis-time. VPC stack needs to lookup the vpc-id provided and determine which subnets to use as well. 

---

## Requirements

1. The VPC must have DNS hostname and DNS resolution support. Otherwise, nodes can't register to your cluster. For more information, see DNS attributes for your VPC in the Amazon VPC User Guide.

2. Support envelope encryption for EKS via KMS.

3. 
---

## Considerations 

1. Resources deployed by EKS have random characters appended to resource names. This may require some heavy configurations to control, but currently requires possible `wildcard` policy actions to support.

2. In CDK v2 you'll need to update any v1 core.* modules to instead be imported as a top level module from aws_cdk. You'll also import the constructs module from the Construct package. 

---