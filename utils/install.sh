#!/bin/bash

Red='\033[0;91m'
Cyan='\033[0;36m'
NC='\033[0m' # No Color
BYellow='\033[1;33m'
IGreen='\033[0;92m'

echo_cyan() {
    printf "${Cyan}${@}${NC}"
}

echo_red() {
    printf "${Red}${@}${NC}"
}

echo_yellow() {
    printf "${BYellow}${@}${NC}"
}

echo_green() {
    printf "${IGreen}${@}${NC}"
}

check_credentials_file() {
    if [ -f "${HOME}/.aws/credentials" ]; then
        return 0
    else
        return 1
    fi
}



# Zero out the .env file
echo "" > .env-customer

# Prompt user to decide whether to use existing AWS credentials
read -p "Do you want to use existing AWS credentials? (yes/no): " use_existing

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
read -p "Enter your AWS Account ID: " AWS_ACCOUNT_ID

export AWS_REGION
echo "AWS_REGION=$AWS_REGION" >> .env-customer
export AWS_ACCOUNT_ID
echo "AWS_ACCOUNT_ID=$AWS_ACCOUNT_ID" >> .env-customer

# Verify AWS credentials
if aws sts get-caller-identity --dry-run > /dev/null 2>&1; then
    output=$(aws sts get-caller-identity --output json)
    if [[ $(jq -r '.UserId' <<< "$output") != null ]] && [[ $(jq -r '.Account' <<< "$output") != null ]] && [[ $(jq -r '.Arn' <<< "$output") != null ]]; then
        echo "Success: AWS credentials verified."
    else
        echo "Error: Not able to determine credentials."
    fi
else
    echo "Error: Not able to determine credentials."
fi

read -p "Enter your AWS ECR Repo URL: " AWS_ECR_REPO_URL
if aws ecr describe-repositories --repository-names $AWS_ECR_REPO_URL > /dev/null 2>&1; then
    export AWS_ECR_REPO_URL
    echo "AWS_ECR_REPO_URL=$AWS_ECR_REPO_URL" >> .env-customer
else
    echo "Error: Invalid AWS ECR Repo URL."
fi

read -p "Enter your AWS Certificate ARN: " AWS_CERTIFICATE_ARN
if aws acm describe-certificate --certificate-arn $AWS_CERTIFICATE_ARN > /dev/null 2>&1; then
    export AWS_CERTIFICATE_ARN
    echo "AWS_CERTIFICATE_ARN=$AWS_CERTIFICATE_ARN" >> .env-customer
else
    echo "Error: Invalid AWS Certificate ARN."
fi

read -p "Enter your AWS VPC ID: " AWS_VPC_ID
if aws ec2 describe-vpcs --vpc-ids $AWS_VPC_ID > /dev/null 2>&1; then
    export AWS_VPC_ID
    echo "AWS_VPC_ID=$AWS_VPC_ID" >> .env-customer
else
    echo "Error: Invalid AWS VPC ID."
fi

read -p "Enter your AWS Private Subnet IDs (comma-separated): " AWS_PRIVATE_SUBNET_IDS
IFS=',' read -ra SUBNET_IDS <<< "$AWS_PRIVATE_SUBNET_IDS"
for i in "${SUBNET_IDS[@]}"; do
    if ! aws ec2 describe-subnets --subnet-ids $i > /dev/null 2>&1; then
        echo "Error: Invalid AWS Private Subnet ID: $i."
        exit 1
    fi
done
export AWS_PRIVATE_SUBNET_IDS
echo "AWS_PRIVATE_SUBNET_IDS=$AWS_PRIVATE_SUBNET_IDS" >> .env-customer
