# eks-cdk-project

This project uses python AWS CDK to deploy a private VPC and networking resources, an EKS cluster with Fargate enabled profiles, a Cognito pool, S3 buckets, Route53 configurations, and deploys helm charts to the resulting cluster.

---

## Requirements

1. The VPC must have DNS hostname and DNS resolution support. Otherwise, nodes can't register to your cluster. For more information, see DNS attributes for your VPC in the Amazon VPC User Guide.

2. Support envelope encryption for EKS via KMS.

3. Use an existing VPC from the customer if passed in as a parameter input during synthesis-time. VPC stack needs to lookup the vpc-id provided and determine which subnets to use as well. 

---

## Reference Material

1. [AWS CDK commands](https://github.com/aws/aws-cdk/blob/main/packages/aws-cdk/README.md)

2. [Parameter types in CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html#parameters-section-structure-grouping)

3. [CDK v2 Fargate Cluster](https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_eks/FargateCluster.html)

4. [CDK Contexts](https://github.com/awsdocs/aws-cdk-guide/blob/main/v2/context.md)

5. [CDK inner workings](https://github.com/Sceptre/sceptre-cdk-handler/blob/61f347a3a30d7073d6dbd539db1e84c9c4df01f6/README.md)


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

- [X] ~~Is it possible to not use lookup or from functions to determine the parameter types? User passes in vpc string and subnet lists string, and we convert to the correct types to use for the FargateCluster construct?~~ No.

- [X] ~~Bootstrapless CDK - to hand a customer a self-deployable template to deploy to their account, ECR repo will already exist, and customer will provide a certificate.~~ Bootstrapless isn't really what it seems. It does without assets, but assets at some level are still needed for the cdk project to be deployed. Skip.

- [ ] Use cert-manager to manage certs? - short lived private ACM? Or just have customer provide a cert, and we create self-signed for internal uses

- [ ] How does the kubectl layer work? So far we get a lambda + layer deployed, but what else is required? Do we even need it, if we're going to deploy manifests/charts to kubernetes in CDK/CDK8s?

- [ ] Use cdk-nag https://github.com/cdklabs/cdk-nag

- [ ] How can EKS pull ECR images with the authentication token or ECR auth? Can we do this during the cdk8s stack deployment?

---

## Future

1. Using distroless images to support services. 
2. Nitro images with provide out of the box node-to-node encryption, not pod-to-pod.
3. Apprunner possibilities.


