# eks-cdk-project

## Motivation

This project uses python AWS CDK to deploy a private VPC and networking resources, an EKS cluster with Fargate enabled profiles, S3 buckets, a RDS Aurora cluster, and deploys a number of helm charts to the EKS cluster. This project is intended to work in a "fully-isolated" or "air-gapped" networking environment. 


## CDK 

Please read the [CDK Docs](docs/cdk.md) for more information on what CDK is and how it's being implemented in this project.

---

## Deployment Control Flow

Here are the inputs available to configure the CDK deployment (_configured in your .env file_):

Variable Name|Description|Default Value|Required|Type|
---|---|---|---|---|
`AWS_PROFILE`|The name of the AWS profile to use from your `~/.aws/credentials` file.|None|Optional|Customer|
`AWS_REGION`|The AWS region where resources will be deployed.|None|Yes|Customer|
`AWS_ACCOUNT_ID`|Your AWS account ID.|None|Yes|Customer|
`AWS_ECR_REPO_URL`|The URL of the ECR repository where images are shared with the respective AWS account.|None|Yes|Customer|
`AWS_CERTIFICATE_ARN`|The ARN of the ACM certificate to use for the ALB.|None|Yes|Customer|
`AWS_INIT_KMS_ARN`|The ARN for the KMS key that the init app will use.|None|Yes|Customer|
`DEPLOY_VPC_STACK`|Whether to deploy the VPC stack or not.|"true"|Optional|Customer|
`AWS_VPC_ID`|The ID of the VPC where the ALB and ECS cluster will be deployed.|None|Yes|Customer|
`AWS_PRIVATE_SUBNET_IDS`|A comma-separated list of subnet IDs.|None|Yes|Customer|
`AWS_KMS_EKS_KEY_ARN`|The ARN of the KMS key for EKS.|None|Yes|Customer|
`AWS_KMS_EFS_KEY_ARN`|The ARN of the KMS key for EFS.|None|Yes|Customer|
`AWS_KMS_RDS_KEY_ARN`|The ARN of the KMS key for RDS.|None|Yes|Customer|
`STACK_STAGE`|The stage of the stack.|"alpha"|Optional|Development|
`STACK_PREFIX`|The prefix of the stack.|"tkp"|Optional|Development|
`STACK_SUFFIX`|The affix of the stack.|"rev7"|Optional|Development|
`DEFAULT_DATABASE_NAME`|The default name of the database.|""|Optional|Development|
`DEFAULT_DATABASE_USERNAME`|The default username of the database.|""|Optional|Development|

---

## Getting Started

1. Use the `.env` template file and fill out **required** inputs and any others depending on what you are testing.

        cp .env.template .env

2. Build and Run deployment container. 

    From the root of the project you can run: 

        make dev

    This will build and run a container for you locally, that will trigger the entrypoint. This entrypoint is an interactive script that allows a user to input values specific to their environment. You can always say `no` which will drop you to the default shell on the container image. You can then run any `make` commands that are available in the `Makefile` or any CDK commands. The container will have all dependencies installed, built, and set up appropriately for consumption. 

    Running `make dev` will also mount the project root directory onto the container. **This is for development purposes**. You can make changes to your CDK code and test your changes by running commands on the container. This should speed up the development feedback loop. 

3. Execute `make` commands or `CDK` commands.

4. Test your changes.

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