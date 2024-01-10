# eks-cdk-project

This project uses python AWS CDK to deploy a private VPC and networking resources, an EKS cluster with Fargate enabled profiles, S3 buckets, a RDS Aurora cluster, and deploys a number of helm charts to the EKS cluster. This project is intended to work in a "fully-isolated" or "air-gapped" networking environment. 

---

## Deployment Control Flow

---

## Getting Started

1. Build and Run deployment container. 

From the root of the project you can run: 

`make dev`

This will build and run a container for you locally, that will trigger the entrypoint. This entrypoint is an interactive script that allows a user to input values specific to their environment. You can always say `no` which will drop you to the default shell on the container image. You can then run any `make` commands that are available in the `Makefile` or any CDK commands. The container will have all dependencies installed, built, and set up appropriately for consumption. 

Running `make dev` will also mount the project root directory onto the container. **This is for development purposes**. You can make changes to your CDK code and test your changes by running commands on the container. This should speed up the development feedback loop. 

2. Execute `make` commands or `CDK` commands.

3. Test your changes.

---

## Reference Material

1. [AWS CDK commands](https://github.com/aws/aws-cdk/blob/main/packages/aws-cdk/README.md)

2. [Parameter types in CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html#parameters-section-structure-grouping)

3. [CDK v2 Fargate Cluster](https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_eks/FargateCluster.html)

4. [CDK Contexts](https://github.com/awsdocs/aws-cdk-guide/blob/main/v2/context.md)

5. [CDK inner workings](https://github.com/Sceptre/sceptre-cdk-handler/blob/61f347a3a30d7073d6dbd539db1e84c9c4df01f6/README.md)

---

## Considerations 

1. Resources deployed by EKS have random characters appended to resource names. This may require some heavy configurations to control, but currently requires possible `wildcard` policy actions to support.

2. In CDK v2 you'll need to update any v1 core.* modules to instead be imported as a top level module from aws_cdk. You'll also import the constructs module from the Construct package. [REF](https://docs.aws.amazon.com/cdk/v2/guide/migrating-v2.html)

3. AWS CDK v2 consolidates the stable parts of the AWS Construct Library, including the core library, into a single package, aws-cdk-lib. Developers no longer need to install additional packages for the individual AWS services they use. This single-package approach also means that you don't have to synchronize the versions of the various CDK library packages.

4. The CDK produces a `kubectl` lambda layer to perform `helm` and `kubectl` commands on the cluster, instead of an operator. Read more [here](docs/kubectl-lambda-layer.md)

5. A limitation of the current implementation is that eksctl initially creates the cluster with both public and private endpoint access enabled, **and disables public endpoint access after all operations have completed.** This is required because eksctl needs access to the Kubernetes API server to allow self-managed nodes to join the cluster and to support GitOps and Fargate. After these operations have completed, eksctl switches the cluster endpoint access to private-only. This additional update does mean that creation of a fully-private cluster will take longer than for a standard cluster. In the future, eksctl may switch to a VPC-enabled Lambda function to perform these API operations.
---