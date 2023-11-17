#!/bin/bash

# Zero out the .env file
echo "" > .env-customer

# motd add here with specific language
echo "This script will help you set up your AWS credentials and configurations required for deployment!"
sleep 1
echo "You have two options for setup:"
echo "1. Interactive setup: This script will guide you through the process of setting up your AWS credentials and configurations."
echo "2. Manual setup: You will be taken to the shell in the container. You will need to manually update the .env file with the required values before deployment."
echo "Please note that the manual setup does not check if every parameter or AWS credentials are set correctly."
read -p "Do you want to proceed with the interactive setup? [yes/no] (default: yes): " setup_choice
if [[ $setup_choice != "yes" ]]; then
    echo "You have chosen the manual setup. Please update the .env file before deployment."
    exit 1
fi


function prompt_aws_credentials() {
    # Prompt user to decide whether to use existing AWS credentials
    read -p "Do you want to use existing AWS credentials? [yes/no] (default: no): " use_existing

    if [[ $use_existing == "yes" ]]; then
        # Use existing AWS credentials
        read -p "Enter the AWS_PROFILE to use: " AWS_PROFILE
        export AWS_PROFILE
        echo "AWS_PROFILE=$AWS_PROFILE" >> .env-customer
    else
        # Set new AWS credentials
        read -p "Enter your AWS Access Key ID: " AWS_ACCESS_KEY_ID
        read -p "Enter your AWS Secret Access Key: " AWS_SECRET_ACCESS_KEY
        read -p "Enter your AWS Session Token (optional): " AWS_SESSION_TOKEN

        export AWS_ACCESS_KEY_ID
        echo "AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID" >> .env-customer
        export AWS_SECRET_ACCESS_KEY
        echo "AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY" >> .env-customer
        export AWS_SESSION_TOKEN
        echo "AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN" >> .env-customer
        echo "Creating a default profile based on the provided credentials..."
        echo "[default]" >> ~/.aws/config
    fi

    # Set AWS region and account ID
    read -p "Enter the AWS region for deployment: " AWS_REGION
    read -p "Enter your AWS Account ID for deployment: " AWS_ACCOUNT_ID

    export AWS_REGION
    echo "AWS_REGION=$AWS_REGION" >> .env-customer
    export AWS_ACCOUNT_ID
    echo "AWS_ACCOUNT_ID=$AWS_ACCOUNT_ID" >> .env-customer
}

check_credentials() {
    # Verify AWS credentials
    if aws sts get-caller-identity --profile "$AWS_PROFILE" --dry-run > /dev/null 2>&1; then
        output=$(aws sts get-caller-identity --profile "$AWS_PROFILE" --output json)
        if [[ $(jq -r '.UserId' <<< "$output") != null ]] && [[ $(jq -r '.Account' <<< "$output") != null ]] && [[ $(jq -r '.Arn' <<< "$output") != null ]]; then
            echo "Success: AWS credentials verified."
            return 0
        else
            echo "Error: Not able to determine credentials."
            read -p "Do you want to retry setting up your AWS credentials? [yes/no] (default: no): " retry
            if [[ $retry == "yes" ]]; then
                prompt_aws_credentials
                check_credentials
            else
                return 1
            fi
        fi
    else
        echo "Error: Not able to determine credentials."
        read -p "Do you want to retry setting up your AWS credentials? [yes/no] (default: no): " retry
        if [[ $retry == "yes" ]]; then
            prompt_aws_credentials
            check_credentials
        else
            return 1
        fi
    fi
}

function prompt_aws_ecr_repo_url() {
    read -p "Enter your AWS ECR Repo URL: (private ECR url is required to pull images from)" AWS_ECR_REPO_URL
    if aws ecr describe-repositories --repository-names "$AWS_ECR_REPO_URL" --profile "$AWS_PROFILE" --region "$AWS_REGION" > /dev/null 2>&1; then
        export AWS_ECR_REPO_URL
        echo "AWS_ECR_REPO_URL=$AWS_ECR_REPO_URL" >> .env-customer
        return 0
    else
        echo "Error: Invalid AWS ECR Repo URL."
        return 1
    fi
}

function prompt_aws_certificate_arn() {
    read -p "Enter your AWS Certificate ARN: " AWS_CERTIFICATE_ARN
    if aws acm describe-certificate --certificate-arn "$AWS_CERTIFICATE_ARN" --profile "$AWS_PROFILE" --region "$AWS_REGION" > /dev/null 2>&1; then
        export AWS_CERTIFICATE_ARN
        echo "AWS_CERTIFICATE_ARN=$AWS_CERTIFICATE_ARN" >> .env-customer
        return 0
    else
        echo "Error: Invalid AWS Certificate ARN."
        return 1
    fi
}

function prompt_aws_eks_kms_arn() {
    read -p "Enter your KMS ARN for encrypting the EKS cluster (optional, if not provided, a new KMS key creation will be attempted): " AWS_EKS_KMS_ARN
    if aws kms describe-key --key-id "$AWS_EKS_KMS_ARN" --profile "$AWS_PROFILE" --region "$AWS_REGION" > /dev/null 2>&1; then
        export AWS_EKS_KMS_ARN
        echo "AWS_EKS_KMS_ARN=$AWS_EKS_KMS_ARN" >> .env-customer
        return 0
    else
        echo "Error: Invalid AWS KMS ARN."
        return 1
    fi
}

function prompt_aws_vpc_id() {
    read -p "Enter your AWS VPC ID (where infrastructure will be provisioned): " AWS_VPC_ID
    if aws ec2 describe-vpcs --vpc-ids "$AWS_VPC_ID" --profile "$AWS_PROFILE" --region "$AWS_REGION" > /dev/null 2>&1; then
        export AWS_VPC_ID
        echo "AWS_VPC_ID=$AWS_VPC_ID" >> .env-customer
        return 0
    else
        echo "Error: Invalid AWS VPC ID."
        return 1
    fi
}

function prompt_aws_private_subnet_ids() {
    read -p "Enter your AWS Private Subnet IDs (comma-separated): " AWS_PRIVATE_SUBNET_IDS
    IFS=',' read -ra SUBNET_IDS <<< "$AWS_PRIVATE_SUBNET_IDS"
    for i in "${SUBNET_IDS[@]}"; do
        if ! aws ec2 describe-subnets --subnet-ids $i --profile "$AWS_PROFILE" --region "$AWS_REGION" > /dev/null 2>&1; then
            echo "Error: Invalid AWS Private Subnet ID: $i."
            return 1
        fi
    done
    export AWS_PRIVATE_SUBNET_IDS
    echo "AWS_PRIVATE_SUBNET_IDS=$AWS_PRIVATE_SUBNET_IDS" >> .env-customer
    return 0
}

function main() {
    while ! prompt_aws_credentials; do 
        if prompt_aws_credentials; then
            echo "Setting AWS credentials, region, and account_id checks were successful!"
        fi
    done
    while ! check_credentials; do 
        if check_credentials; then
            echo "Credentials retrieval check was successful!"
        fi
    done
    while ! prompt_aws_ecr_repo_url; do 
        if prompt_aws_ecr_repo_url; then
            echo "ECR Repository URL check was successful!"
        fi
    done
    while ! prompt_aws_certificate_arn; do 
        if prompt_aws_certificate_arn; then
            echo "Certificate ARN lookup check was successful!"
        fi
    done
    while ! prompt_aws_eks_kms_arn; do 
        if prompt_aws_eks_kms_arn; then
            echo "KMS ARN lookup was successful!"
        fi
    done
    while ! prompt_aws_vpc_id; do 
        if prompt_aws_vpc_id; then
            echo "VPC ID lookup was successful!"
        fi
    done
    while ! prompt_aws_private_subnet_ids; do 
        if prompt_aws_private_subnet_ids; then
            echo "SUBNET IDs lookup was successful!"
        fi
    done
    echo "Success: All prompts were checked and successful!"

    
}

main
