# Video Demo 

1. Get AWS SSO Credentials or Credential Chain 

In this demo we will use an existing VPC and resources provided by the customer and provision infrastructure using CDK.

2. Authenticate to ECR:

        aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 728168703404.dkr.ecr.us-west-2.amazonaws.com

3. Pull image from ECR to local via docker pull 
    
        docker pull 728168703404.dkr.ecr.us-west-2.amazonaws.com/c1-tkp-cdk:v0.0.7

4. Run the docker container
        
        docker run -v /${HOME}/.aws:/home/cdk/.aws -v ${PWD}:/app/logs -it 728168703404.dkr.ecr.us-west-2.amazonaws.com/c1-tkp-cdk:v0.0.7

5. Interactive script runs

        default
        us-west-2
        728168703404

6. Fill in the values:
        
        vpc: vpc-0b086c1c600e041ba
        
        subnets: subnet-0bdcb6ba470c1b143,subnet-087f89c5ef9432ebb,subnet-0668613100aea4def,subnet-0c6ec51de876c0127
        
        ecr_repo: 728168703404.dkr.ecr.us-west-2.amazonaws.com
        
        certificate arn: arn:aws:acm:us-west-2:728168703404:certificate/d1f09e52-6a3f-4ec6-8846-592b168c4ee4


7. have it bootstrap the account (skip)
8. deploy the entire stack

9. There's a lot of room for improvement to ensure the customer / user is less likely to make mistakes. We have work to do in terms of making this interactive script a bit more polished. But alternatively, an experience user could just edit the .env file, and run two commands without having to go through the the prompts.

10. In the console you can see we have multiple stacks created as a part of this deployment. There's also some work to do there to ensure all the CDK code gets deployed appropriately since this is just a condensed version of the entire project.