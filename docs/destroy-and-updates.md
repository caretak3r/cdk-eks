# CDK Destroy and Updates

Destroying and updating resources with AWS CDK involves a set of operations that can either modify existing resources or remove them entirely from the cloud environment. Understanding how these operations work is crucial for maintaining and evolving cloud infrastructure safely and predictably.


## Updates and Destructive Actions

An update in AWS CDK is an operation that applies changes to the existing stack resources. Most updates are non-destructive and can be applied directly, such as updating tags or modifying the configuration of a resource. However, certain updates may require destructive actions, where resources need to be replaced or deleted for the changes to take effect.

Scenarios where an update might require destructive actions include:

- Changing a resource's logical ID: Since the logical ID is used to uniquely identify a resource, changing it will lead to the creation of a new resource and the deletion of the old one.
- Modifying immutable properties: Some resource properties cannot be updated once the resource is created. For example, changing the name of an Amazon S3 bucket requires the creation of a new bucket and migration of data.
- Updating resources with replacement policies: Certain resources have policies that dictate they must be replaced when specific attributes are altered.

When a destructive update is required, AWS CDK will handle the replacement of resources, ensuring that the new resource is created before deleting the old one to minimize downtime.

### Update Considerations

1. Usually an `update` just requires the CDK project to be executed again.

    a. Infrastructure resources _may change_ where a new ResourceId is created (just represents some AWS component) and other stacks will need to be updated in order to incorporate these changes. 

    b. Application resources _may change_ or needs to be updated to a newer or older version. CloudFormation should remove those application deployments (in this case; removing the helm project or manifests) and subsequently deploy the different version. 

2. Application changes should be straightforward, but there may be instances where we cannot cleanly remove a deployment (pod tolerances, taints or cannot be evicted).

3. Infrastructure changes where resources ids change, will likely need a **complete** CDK update. If an application is dependent on an AWS ARN or ResourceId, the application stacks will need a stack update in order to incorporate those changes. This will also likely require redeploying the application stacks to have them take effect. 


### Plan

1. **Update Considerations #3**: We need to implement a "rolling deployment" or "rolling upgrade" configuration to the application and operator pods. This will require some work, as not all application are stateless, and we need to consider how this will work in production. 

2. (_Unlikely strategy in the short term_) Another course of action that we can take is to sync our codebase to the Kubernetes clusters using something like Flux or ArgoCD. This ensures that our codebase changes will update the cluster appropriately, effectively syncing changes from CodeCommit or GitHub to the clusters or CloudFormation stacks ([see CloudFormation git syncs](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/git-sync.html)).

---
## Destroy Operations

The `cdk destroy` command is used to remove a stack and all of its resources from AWS. This operation is irreversible and should be used with caution.

Resources that might need to be retained include:

- Databases or storage systems containing critical data.
- Logs or monitoring data that are required for compliance or auditing purposes.
- Any S3 data captured

To retain a resource during a destroy operation, you can set the `RemovalPolicy` attribute on the resource to `Retain`. This instructs AWS CDK not to delete the resource when the stack is destroyed.

There are likely resources that will need to be retained, so by setting `RemovalPolicy` to `Destroy` on the different constructs will ensure that a `cdk destroy` will "cleanly" remove resources created.

### Destroy Considerations

### Plan

1. Ensure `constants.py` has the variables to set RemovalPolicy for all the constructs and resources.

2. Some variables will be set to `Retain`, but this requires further discussions with the application teams. 

### Ensuring Deletion of All Resources

To ensure the deletion of all resources during a destroy operation, you can set the `RemovalPolicy` attribute to `Destroy`. This is useful for resources that are safe to delete, such as temporary databases or test environments.

For example, to apply a removal policy to an Amazon S3 bucket in AWS CDK, you would use:
