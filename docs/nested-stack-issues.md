The issue you're experiencing is likely due to the way AWS CDK handles dependencies between stacks. When you define a dependency between two stacks, AWS CDK will try to resolve this dependency by moving resources from one stack to another. This is done to avoid circular dependencies and to ensure that resources are created in the correct order.

In your case, it seems that the AlbStack is dependent on the EksStack. This is evident from the following code in app.py:

```
alb_stack = AlbStack(
    app,
    "AlbStack",
    vpc=base_stack.vpc,
    ecr_repo_url=base_stack.ecr_repo_url,
    cluster=eks_stack.cluster,
    customer_certificate_arn=base_stack.customer_certificate_arn,
    stack_name=f"{constants.STACK_PREFIX}-alb-stack-{constants.STACK_SUFFIX}",
    **env,
)
alb_stack.add_dependency(eks_stack)
```

Here, AlbStack is using the cluster from EksStack, and you're explicitly adding a dependency on EksStack to AlbStack.

Because of this dependency, AWS CDK is moving the resources from AlbStack to EksStack during the synthesis phase. This is why you're seeing the resources in the EksStack CloudFormation template and not in the AlbStack template.

To fix this issue, you need to remove the direct dependency between AlbStack and EksStack. Instead of passing the cluster from EksStack to AlbStack, you can create the cluster in AlbStack itself. This way, AlbStack will not be dependent on EksStack, and AWS CDK will not move the resources.

Here's how you can do it:

```
# In AlbStack
self.cluster = eks.Cluster(self, "Cluster", vpc=self.vpc, ...)
```

Remember to remove the cluster parameter from the AlbStack constructor and the add_dependency call.

Please note that this is a simplified solution. Depending on your use case, you might need to adjust this solution to fit your needs. For example, if you need to share the cluster between multiple stacks, you might need to create a separate stack just for the cluster and make other stacks dependent on this new stack.