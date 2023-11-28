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