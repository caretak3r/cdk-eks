#!/bin/bash

# Define variables
HELM_CHART_NAME="platform"
HELM_CHART_VERSION="0.1.31-kubeview"
ECR_REPO_URL="728168703404.dkr.ecr.us-west-2.amazonaws.com"

# Package the Helm chart
helm package $HELM_CHART_NAME --version $HELM_CHART_VERSION

# Login to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin $ECR_REPO_URL

# Push the Helm chart to ECR
helm push "$HELM_CHART_NAME-$HELM_CHART_VERSION.tgz" "oci://$ECR_REPO_URL/"
