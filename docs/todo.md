## Issues / Todos

- [X] ~~There is no upgradeable version past `aws-cdk.asset-kubectl-v20==2.1.2` (except for v21/v22), to support v27 or v28.~~ (v27 exists but you need to download it from git)

- [X] ~~Is it possible to not use lookup or from functions to determine the parameter types? User passes in vpc string and subnet lists string, and we convert to the correct types to use for the FargateCluster construct?~~ No.

- [X] ~~Bootstrapless CDK - to hand a customer a self-deployable template to deploy to their account, ECR repo will already exist, and customer will provide a certificate.~~ Bootstrapless isn't really what it seems. It does without assets, but assets at some level are still needed for the cdk project to be deployed. Skip.

- [ ] Use cert-manager to manage certs? - short lived private ACM? Or just have customer provide a cert, and we create self-signed for internal uses

- [X] How does the kubectl layer work? So far we get a lambda + layer deployed, but what else is required? Do we even need it, if we're going to deploy manifests/charts to kubernetes in CDK/CDK8s?

- [ ] Use cdk-nag https://github.com/cdklabs/cdk-nag

- [X] How can EKS pull ECR images with the authentication token or ECR auth? Can we do this during the cdk8s stack deployment?

- [X] Place handlers in VPC (place_cluster_handler_in_vpc)[https://github.com/aws/aws-cdk/issues/12171] apparently doesn't work. -.- Even with a VPC Endpoint for EKS. 

- [X] Better aws credentials workflow, prompt user outright for what they need to set? 

- [X] Test running this on EC2, for instance creds

- [ ] Set endpoint to PRIVATE

- [ ] Ensure security groups are set correctly

- [X] ALB not being setup properly?

- [ ] Give a user a fully configured IAM policy or ROLE to use for the cloudformation stack execution - default is AdminAccess 

- [ ] Ensure bootstrap and deploy will use a specific IAM role/policies instead of the default AdministratorAccess

- [ ] Deploy the project as a CodePipeline construct instead of having the user wait on the bootstrap and deployment installs

- [ ] Implement CDK snapshot testing

- [ ] EKS Pod Identity - https://aws.amazon.com/blogs/aws/amazon-eks-pod-identity-simplifies-iam-permissions-for-applications-on-amazon-eks-clusters/

- [ ] Use distroless images

- [ ] Set replicas for pods to 3 for leader election choices, even with 2 subnets

- [ ] generate a unique id, that is used on every cdk invocation that will be used as a tag value for the entire cloudformation stack, and will tag all resources. the unique id will also be used as the folder path in the cdk s3 bucket with all synthesized files and inputs. 

- [ ] VERIFY: Based on this [doc](https://docs.aws.amazon.com/AmazonECR/latest/userguide/registry_auth.html) ECR tokens are valid for 12 hours. During cdk deployment, we can pull images and deploy them without issue. What happens if the services are defined with `AlwaysPull` and EKS needs to pull an image once in production? 
    
    > That works for private ECR in the same account if the AmazonEC2ContainerRegistryReadOnly policy is attached to the worker nodes.
    > https://stackoverflow.com/questions/54109603/how-to-use-docker-image-in-ecr-with-aws-eks
    > No Credentials needed. Workergroup role or FargatePod role should already be provisioned with this.


- [X] Encrypt EKS cluster with provided KMS

- [ ] Encrypt all infra with provided KMS from the customer. Ensure inputs(env) is being used instead of creating one.

- [ ] Associate ACM certificate to ALB controller 

- [ ] Fix the pod names, maybe remove the release name from the `add_helm_chart()`

    ```
    aws-load-balancer-controller-aws-load-balancer-controller-lnk2l   1/1     Running   0          7h40m
    aws-load-balancer-controller-aws-load-balancer-controller-wsw2b   1/1     Running   0          7h40m
    ```
- Update any IAM policies to restrict access on conditions to specific resources the stack creates. 

- [ ] Final account to share images with a customer from, need lead time. 

- [ ] Vertical and Horizontal scaling via Karpenter

- [ ] Pod disruption budgets set to minimize disruption during OS patching by AWS 

- [ ] Provide a bootstrap template, to minimize resources that are created, do we even need the ECR repo created from bootstrap? 

- [ ] Implement EFS 

- [ ] Use Aspects to apply configurations to constructs within a single scope 

- [ ] Ensure IAM roles from the cluster/fargate pod roles are added to the s3 bucket policy

- [ ] Instead of requesting the ecr repo url from the user, we can create it. Since we share artifacts via account replication: 
    - for example you have this ecr_repo_url: 1234567890.dkr.ecr.us-west-2.amazonaws.com
    - we can get the account_id and region of where the stacks are going to be deployed
    - if the user does not provide one, we can assume what it will be and try

- [ ] Use constants.py file to also include other variables like the REPOs that are being shared with a user, versus hardcoding them (because they could change)

