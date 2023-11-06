# eks-cdk-project

This project uses python AWS CDK to deploy a private VPC and networking resources, an EKS cluster with Fargate enabled profiles, a Cognito pool, S3 buckets, Route53 configurations, and deploys helm charts to the resulting cluster.

---

## Todo

1. https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/configure-mutual-tls-authentication-for-applications-running-on-amazon-eks.html

2. https://eksctl.io/usage/kms-encryption/

3. Use an existing VPC from the customer if passed in as a parameter input during synthesis-time. VPC stack needs to lookup the vpc-id provided and determine which subnets to use as well. 

---

## Requirements

1. The VPC must have DNS hostname and DNS resolution support. Otherwise, nodes can't register to your cluster. For more information, see DNS attributes for your VPC in the Amazon VPC User Guide.

2. Support envelope encryption for EKS via KMS.

---

## Considerations 

1. Resources deployed by EKS have random characters appended to resource names. This may require some heavy configurations to control, but currently requires possible `wildcard` policy actions to support.

2. In CDK v2 you'll need to update any v1 core.* modules to instead be imported as a top level module from aws_cdk. You'll also import the constructs module from the Construct package. [REF](https://docs.aws.amazon.com/cdk/v2/guide/migrating-v2.html)

3. AWS CDK v2 consolidates the stable parts of the AWS Construct Library, including the core library, into a single package, aws-cdk-lib. Developers no longer need to install additional packages for the individual AWS services they use. This single-package approach also means that you don't have to synchronize the versions of the various CDK library packages.

4. Not sure if absolutely needed, but CDK by default uses 1.24 of the kubectl lambda layer, which is used on stack updates. Solve this by `pip install aws-cdk.lambda-layer-kubectl-v27` [REF](https://github.com/cdklabs/awscdk-asset-kubectl/tree/kubectl-v24/main)

5. We’ll use boto3 (this is one of the things that I don’t really like about AWS CDK – that a lot of things have to be done not with the methods/constructs of the CDK itself, but with “crutches” in the form of boto3 or other modules/libraries).

6. The CDK produces a `kubectl` lambda layer to perform `helm` and `kubectl` commands on the cluster, instead of an operator. Read more [here](docs/kubectl-lambda-layer.md)

7. A limitation of the current implementation is that eksctl initially creates the cluster with both public and private endpoint access enabled, **and disables public endpoint access after all operations have completed.** This is required because eksctl needs access to the Kubernetes API server to allow self-managed nodes to join the cluster and to support GitOps and Fargate. After these operations have completed, eksctl switches the cluster endpoint access to private-only. This additional update does mean that creation of a fully-private cluster will take longer than for a standard cluster. In the future, eksctl may switch to a VPC-enabled Lambda function to perform these API operations.
---

## Issues / Todos

- [X] ~~There is no upgradeable version past `aws-cdk.asset-kubectl-v20==2.1.2` (except for v21/v22), to support v27 or v28.~~ (v27 exists but you need to download it from git)

---