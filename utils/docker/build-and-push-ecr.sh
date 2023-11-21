#!/bin/bash
DOCKER_IMAGE_NAME="NAME"
AWS_REGION="us-west-2"
AWS_ACCOUNT_ID="728168703404"
ECR_REPO_NAME="NAME"
DOCKERFILE_PATH="Dockerfile.prod"
#IMAGE_TAG=$(aws ecr describe-images --repository-name $ECR_REPO_NAME --region $AWS_REGION --query 'sort_by(imageDetails,& imagePushedAt)[-1].imageTags[0]' --output text)
#NEW_IMAGE_TAG=$((IMAGE_TAG+1))
IMAGE_TAG="tkp-cdk-v0.0.2"

echo "Building Docker image..."
docker build -t $DOCKER_IMAGE_NAME -f $DOCKERFILE_PATH .

echo "Authenticating Docker to AWS ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

echo "Tagging new Docker image version..."
docker tag $DOCKER_IMAGE_NAME:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:$IMAGE_TAG

echo "Pushing Docker image to ECR..."
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:$IMAGE_TAG

echo "Docker image pushed successfully with tag: $IMAGE_TAG"
