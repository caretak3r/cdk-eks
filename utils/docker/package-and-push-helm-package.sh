#!/bin/bash

# Define variables
HELM_CHART_NAME=""
HELM_CHART_VERSION=""
ECR_REPO_URL=""

# Package the Helm chart
helm package $HELM_CHART_NAME --version $HELM_CHART_VERSION

# Login to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin $ECR_REPO_URL

# Push the Helm chart to ECR
helm push "$HELM_CHART_NAME-$HELM_CHART_VERSION.tgz" "oci://$ECR_REPO_URL/"
