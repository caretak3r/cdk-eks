Tokens are placeholders for the resources whose values are only available at a later phase of the deployment process.

We will see a string containing a sequence of random characters if we log the tokens. At the beginning of the deployment, CDK builds the template from the code. At this time, CDK will pass placeholders on to the relevant part of the template code when needed. An example is when we use the imported VPC ID to get the whole VPC object.

At a later stage, when the token’s value (for example, a VPC ID) is available, CDK will replace it with the actual value.

It will only be available at CloudFormation execution time. It’s the last stage when CloudFormation creates or updates the resources that we have defined in the CDK app code. The process will resolve most placeholder (token) values at this phase.