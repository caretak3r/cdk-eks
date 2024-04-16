# VPC Requirements

When a Kubernetes cluster that's version 1.18 and earlier was created, Amazon EKS added the following tag to all of the subnets that were specified.

    Key	Value
    kubernetes.io/cluster/my-cluster	shared

When you create a new Kubernetes cluster now, Amazon EKS doesn't add the tag to your subnets. If the tag was on subnets that were used by a cluster that was previously a version earlier than 1.19, the tag wasn't automatically removed from the subnets when the cluster was updated to a newer version. Version 2.1.1 or earlier of the AWS Load Balancer Controller requires this tag. If you are using a newer version of the Load Balancer Controller, you can remove the tag without interrupting your services.

We're using ALB controller version 2.6.2 and EKS version 1.28. So this does not apply to us.