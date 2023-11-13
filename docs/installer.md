# Installer 

In order to deploy this project some steps need to be followed to ensure this works seamlessly. The docker container will be packaged with all the necessary packages and utilities, and all we require from the user running this is their AWS credentials.

The user should be able to pull the docker image we provide them from AWS Elastic Container Registry, and/or run commands to build, and deploy the CDK project.

Assume customer cannot run docker-compose commands, and instead need to rely on running commands inside the container. 

Customer pulls image.
Customer runs image with mounting `~/.aws` or not if they want to update the .env file.
Customer updates .env file.
Customer runs `make install` which bootstraps and deploys the cdk project.


## Requirements 

1. You will need to have docker or some container management system to interact with our deployment container.

2. You will need the ability to pull our docker image from ECR, which has been shared with you. You can do that with the following: 

    ```
    aws ecr get-login-password --region region | docker login --username AWS --password-stdin aws_account_id.dkr.ecr.region.amazonaws.com
    ```


1. Please set your AWS credentials in your local or cloud environment. 

    However you retrieve your credentials, the docker image will mount your `~/.aws` (on Linux or Mac) or `C:\Users\username\.aws` (if you're using windows).

    Alternatively, you can set the credentials using the provided `.env` file. This file is where your inputs will be configured. 

    **Remember**: If you set your credentials in the `.env` file, it will override the credentials set in your `~/.aws/credentials` file.

2. Configure inputs 

    In the provided `.env` file, fill out the required environment variables that will be used to deploy the project. 

        # AWS Environment Variables (required)
        AWS_PROFILE=""
        AWS_REGION=""
        AWS_ACCOUNT_ID=""

        # AWS Credentials (optional, if you're using your ~/.aws/credentials file)
        AWS_ACCESS_KEY_ID=""
        AWS_SECRET_ACCESS_KEY=""
        AWS_SESSION_TOKEN=""

        # AWS Resources (required)
        AWS_ECR_REPO_URL=""
        AWS_CERTIFICATE_ARN=""
        AWS_VPC_ID=""
        AWS_PRIVATE_SUBNET_IDS="" # Please set this as a comma-separated list of subnet IDs, e.g. "subnet-12345678,subnet-87654321"
    
3. Use the provided `make` file or the alternative commands to deploy this project. 

    1. `make build`
    2. `make deploy`
        
        a. If your AWS credentials, Environment Variables, and access to the AWS account you are using are all set up properly, this will begin to deploy the project.


## Commands 

Here are some commands you can run depending on your use case. 

| Command      | Description | Details     |
| :---        |  :----   |          ---: |
| make copy      | Copy the CloudFormation templates and assets to the host.       | Generated CloudFormation templates and assets will be copied from the container to the host directory called `outputs`.   |