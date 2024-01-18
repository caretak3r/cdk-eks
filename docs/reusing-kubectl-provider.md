# Kubectl Provider Reuse 

There seems to be multiple ways to re-use a KubectlProvider created by the EKS L2 construct.
 

To reuse the KubectlProvider within an AWS CDK project in Python, you can use the KubectlProvider class from the aws_cdk.aws_eks package. Here's a general outline of how to achieve this:
Import the KubectlProvider: Import the KubectlProvider for the existing EKS cluster using the from_kubectl_provider_attributes method.
Use the KubectlProvider: Once you have imported the KubectlProvider, you can use it to perform kubectl operations against the cluster within your CDK project.
Here's an example of how you can achieve this:

```
from aws_cdk import core
from aws_cdk.aws_eks import KubectlProvider, Cluster

# Assuming you have the necessary attributes for the KubectlProvider
kubectl_provider = KubectlProvider.from_kubectl_provider_attributes(
    self, 'KubectlProvider',
    function_arn='your-function-arn',
    kubectl_role_arn='your-kubectl-role-arn',
    handler_role=your_handler_role
)

# Then you can use the kubectl_provider to perform kubectl operations
# For example, you can use it with an EKS cluster imported using Cluster.from_cluster_attributes
cluster = Cluster.from_cluster_attributes(
    self, 'ImportedCluster',
    cluster_name='your-cluster-name',
    kubectl_provider=kubectl_provider
)
```

By following these steps, you can reuse the KubectlProvider for an imported EKS cluster within your AWS CDK project in Python.

At the minimum, when importing clusters for kubectl management, you will need to specify:

clusterName - the name of the cluster.
kubectlRoleArn - the ARN of an IAM role mapped to the system:masters RBAC role. If the cluster you are importing was created using the AWS CDK, the CloudFormation stack has an output that includes an IAM role that can be used. Otherwise, you can create an IAM role and map it to system:masters manually. The trust policy of this role should include the the arn:aws::iam::${accountId}:root principal in order to allow the execution role of the kubectl resource to assume it.
If the cluster is configured with private-only or private and restricted public Kubernetes endpoint access, you must also specify:

kubectlSecurityGroupId - the ID of an EC2 security group that is allowed connections to the cluster's control security group. For example, the EKS managed cluster security group.
kubectlPrivateSubnetIds - a list of private VPC subnets IDs that will be used to access the Kubernetes endpoint.

Another way: 

### Kubectl Provider 

1. Other Constructs like EKS we need to tell it several of the parameters for it to reconstruct the object. Here we need to tell it a few things like the `open_id_connect_provider`, the `kubectl_role_arn`, etc. for it to give us an object we can call/use like we'd created the EKS cluster in *this* template. 

We pass these parameters across our Stacks using CloudFormation Exports (Outputs in one CF stack we can reference in another):

Here is an example of exporting the things we need in eks_cluster.py
```
core.CfnOutput(
    self, "EKSClusterName",
    value=eks_cluster.cluster_name,
    description="The name of the EKS Cluster",
    export_name="EKSClusterName"
)
```

And here is an example of importing them in ghost_example.py to reconstitute an eks.Cluster object from the required attributes.
```
eks_cluster = eks.Cluster.from_cluster_attributes(
  self, "cluster",
  cluster_name=core.Fn.import_value("EKSClusterName"),
  open_id_connect_provider=eks.OpenIdConnectProvider.from_open_id_connect_provider_arn(
    self, "EKSClusterOIDCProvider",
    open_id_connect_provider_arn = core.Fn.import_value("EKSClusterOIDCProviderARN")
  ),
  kubectl_role_arn=core.Fn.import_value("EKSClusterKubectlRoleARN"),
  vpc=vpc,
  kubectl_security_group_id=core.Fn.import_value("EKSSGID"),
  kubectl_private_subnet_ids=[vpc.private_subnets[0].subnet_id, vpc.private_subnets[1].subnet_id]
)
```