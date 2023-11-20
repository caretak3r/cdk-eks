#!/bin/bash
trap 'echo "\n Script interrupted by user. Returning to shell."; exit' INT
export trap

function prompt_aws_credentials() {
    # Prompt user to decide whether to use existing AWS credentials
    read -p "Do you want to use existing AWS credentials? [yes/no]: " use_existing

    if [[ $use_existing == "yes" ]]; then
        # Use existing AWS credentials
        read -p "Enter the AWS_PROFILE to use: " AWS_PROFILE
        export AWS_PROFILE
        sed -i "s/^AWS_PROFILE=.*/AWS_PROFILE=$AWS_PROFILE/" .env
    else
        # Set new AWS credentials
        read -p "Enter your AWS Access Key ID: " AWS_ACCESS_KEY_ID
        read -p "Enter your AWS Secret Access Key: " AWS_SECRET_ACCESS_KEY
        read -p "Enter your AWS Session Token (optional): " AWS_SESSION_TOKEN

        export AWS_ACCESS_KEY_ID
        sed -i "s/^AWS_ACCESS_KEY_ID=.*/AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID/" .env
        export AWS_SECRET_ACCESS_KEY
        sed -i "s/^AWS_SECRET_ACCESS_KEY=.*/AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY/" .env
        export AWS_SESSION_TOKEN
        sed -i "s/^AWS_SESSION_TOKEN=.*/AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN/" .env
    fi

    # Set AWS region and account ID
    read -p "Enter the AWS region for deployment: " AWS_REGION
    read -p "Enter your AWS Account ID for deployment: " AWS_ACCOUNT_ID

    export AWS_REGION
    sed -i "s/^AWS_REGION=.*/AWS_REGION=$AWS_REGION/" .env
    export AWS_ACCOUNT_ID
    sed -i "s/^AWS_ACCOUNT_ID=.*/AWS_ACCOUNT_ID=$AWS_ACCOUNT_ID/" .env
}

function check_credentials() {
    # Verify AWS credentials
    if aws sts get-caller-identity --profile "$AWS_PROFILE" > /dev/null 2>&1; then
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
                echo "Returning you to a shell."
                /bin/bash
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
    read -p "Enter your AWS ECR Repo URI (private ECR uri looks like: 728168703404.dkr.ecr.us-west-2.amazonaws.com/platform): " AWS_ECR_REPO_URL
    REPO_LIST=$(aws ecr describe-repositories --profile "$AWS_PROFILE" --region "$AWS_REGION" --output json | jq -r '.repositories[].repositoryUri')
    if echo "$REPO_LIST" | grep -q "$AWS_ECR_REPO_URL"; then
        export AWS_ECR_REPO_URL
        ESCAPED_AWS_ECR_REPO_URL=$(printf '%s\n' "$AWS_ECR_REPO_URL" | sed 's:[\/&]:\\&:g;$!s/$/\\/')
        sed -i "s/^AWS_ECR_REPO_URL=.*/AWS_ECR_REPO_URL=$ESCAPED_AWS_ECR_REPO_URL/" .env
        return 0
    else
        echo "Error: Invalid AWS ECR Repo URL."
        return 1
    fi
}

function prompt_aws_certificate_arn() {
    read -p "Enter your AWS Certificate ARN (ex: arn:aws:acm:us-west-2:728168703404:certificate/d1f09e52-6a3f-4ec6-8846-592b168c4ee4): " AWS_CERTIFICATE_ARN
    if aws acm describe-certificate --certificate-arn "$AWS_CERTIFICATE_ARN" --profile "$AWS_PROFILE" --region "$AWS_REGION" > /dev/null 2>&1; then
        export AWS_CERTIFICATE_ARN
        ESCAPED_AWS_CERTIFICATE_ARN=$(printf '%s\n' "$AWS_CERTIFICATE_ARN" | sed 's:[\/&]:\\&:g;$!s/$/\\/')
        sed -i "s/^AWS_CERTIFICATE_ARN=.*/AWS_CERTIFICATE_ARN=$ESCAPED_AWS_CERTIFICATE_ARN/" .env
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
        ESCAPED_AWS_EKS_KMS_ARN=$(printf '%s\n' "$AWS_EKS_KMS_ARN" | sed 's:[\/&]:\\&:g;$!s/$/\\/')
        sed -i "s/^AWS_EKS_KMS_ARN=.*/AWS_EKS_KMS_ARN=$ESCAPED_AWS_EKS_KMS_ARN/" .env
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
        sed -i "s/^AWS_VPC_ID=.*/AWS_VPC_ID=$AWS_VPC_ID/" .env
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
    sed -i "s/^AWS_PRIVATE_SUBNET_IDS=.*/AWS_PRIVATE_SUBNET_IDS=$AWS_PRIVATE_SUBNET_IDS/" .env
    return 0
}

function prompt_bootstrap_environment() {
    read -p "Do you want to proceed to bootstrapping the target AWS environment? [yes/no] (default: no): " proceed_bootstrap
    if [[ $proceed_bootstrap == "yes" ]]; then
        echo "Proceeding to bootstrap the target AWS environment..."
        if make bootstrap > bootstrap.log 2>&1; then
            echo "Bootstrap successful!"
            return 0
        else
            echo "Bootstrap failed. Check bootstrap.log for details."
            echo "Printing .env file values and error message to bootstrap.log..."
            cat .env >> bootstrap.log
            echo "Error message from 'make bootstrap':" >> bootstrap.log
            tail -n 5 bootstrap.log >> bootstrap.log
            return 1
        fi
    else
        echo "Skipping bootstrapping the target AWS environment."
        return 0
    fi
}

function prompt_deploy_environment() {
    read -p "Do you want to proceed to deploying to the target AWS environment? [yes/no] (default: no): " proceed_deploy
    if [[ $proceed_deploy == "yes" ]]; then
        echo "Proceeding to deploy the target AWS environment..."
        if make deploy > deploy.log 2>&1; then
            echo "Deployment successful!"
            return 0
        else
            echo "Deployment failed. Check deploy.log for details."
            echo "Printing .env file values and error message to deploy.log..."
            cat .env >> deploy.log
            echo "Error message from 'make deploy':" >> deploy.log
            tail -n 5 deploy.log >> deploy.log
            return 1
        fi
    else
        echo "Skipping deploying the target AWS environment."
        return 0
    fi
}

function confirm_and_modify_variables() {
    while true; do
        echo "Printing .env file values:"
        cat .env
        echo "Menu:"
        echo "1. Modify variables"
        echo "2. Bootstrap only"
        echo "3. Deploy only"
        echo "4. Cancel"
        read -p "Select an option: " menu_option
        case $menu_option in
            1)
                read -p "Enter the variable you want to modify: " variable_name
                read -p "Enter the new value for $variable_name: " variable_value
                sed -i "s/^$variable_name=.*/$variable_name=$variable_value/" .env
                ;;
            2)
                echo "Proceeding to bootstrap..."
                if prompt_bootstrap_environment; then
                    echo "Bootstrap successful!"
                    return 0
                else
                    echo "Bootstrap failed. Check the logs for details."
                    return 1
                fi
                ;;
            3)
                echo "Proceeding to deploy..."
                if prompt_deploy_environment; then
                    echo "Deployment successful!"
                    return 0
                else
                    echo "Deployment failed. Check the logs for details."
                    return 1
                fi
                ;;
            4)
                echo "You have chosen to cancel. We're giving you a shell. Please confirm that your .env file is configured as you expect."
                echo "You can manually run 'make bootstrap' followed by 'make deploy'."
                /bin/bash
                return 0
                ;;
            *)
                echo "Invalid option. Please select a valid option."
                ;;
        esac
    done
}


function main() {
    # motd add here with specific language
    echo "This script will help you set up your AWS credentials and configurations required for deployment!"
    sleep 1
    echo ""
    echo "You have two options for setup:"
    echo "1. Interactive setup: This script will guide you through the process of setting up your AWS credentials and configurations."
    echo "2. Manual setup: You will be taken to the shell in the container. You will need to manually update the .env file with the required values before deployment."
    echo "WARNING: Please note that the manual setup does not check if every parameter or AWS credentials are set correctly."
    echo ""
    read -p "Do you want to proceed with the interactive setup? [yes/no]: " setup_choice
    if [[ $setup_choice != "yes" ]]; then
        echo "You have chosen the manual setup. Please update the .env file before deployment."
        /bin/bash
    fi

    # use .env.template
    cp .env.template .env


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
    # while ! prompt_aws_eks_kms_arn; do 
    #     if prompt_aws_eks_kms_arn; then
    #         echo "KMS ARN lookup was successful!"
    #     fi
    # done
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

    while ! confirm_and_modify_variables; do 
        if confirm_and_modify_variables; then
            echo "Variable modification was successful!"
        fi
    done
}

# main function call
main

