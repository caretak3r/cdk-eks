
`from_vpc_attributes()`

NOTE: using fromVpcAttributes() with deploy-time parameters (like a Fn.importValue() or CfnParameter to represent a list of subnet IDs) sometimes accidentally works. It happens to work for constructs that need a list of subnets (like AutoScalingGroup and eks.Cluster) but it does not work for constructs that need individual subnets (like Instance). See https://github.com/aws/aws-cdk/issues/4118 for more information.


`from_lookup`

Calling this method will lead to a lookup when the CDK CLI is executed. You can therefore not use any values that will only be available at CloudFormation execution time (i.e., Tokens). 

The VPC information will be cached in cdk.context.json and the same VPC will be used on future runs. To refresh the lookup, you will have to evict the value from the cache using the cdk context command. See https://docs.aws.amazon.com/cdk/latest/guide/context.html for more information.

