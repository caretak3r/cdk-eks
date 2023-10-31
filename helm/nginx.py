# Create an nginx cdk8s app
# Path: helm/nginx.py
from constructs import Construct
from cdk8s import Chart
from imports import k8s
from cdk8s_plus import (
    ChartInfo,
    ChartVersion,
    Helm,
    HelmChart,
    HelmChartOptions,
    HelmRepository,
    HelmRepositoryOptions,
)
from aws_cdk import aws_iam as iam
from aws_cdk import aws_ec2 as ec2
