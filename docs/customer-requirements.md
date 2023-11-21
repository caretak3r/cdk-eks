# Customer Requirements

We support the creation of fully-private clusters that have no outbound internet access and have only private subnets. VPC endpoints are used to enable private access to AWS services.

This guide describes how to create a "zero-trust" networking environment in AWS. 


## AWS Infrastructure

1. Virtual Private Cloud (VPC)
2. Subnets
3. Route Tables
4. VPC Endpoints
5. IAM Permissions
6. Elastic Container Repository (ECR)


## AWS Network Setup

### Private Virtual Private Cloud (VPC)

To create a fully private VPC with DNS hostnames and DNS resolution enabled, follow the steps below:

   - Navigate to the VPC Dashboard in the AWS Management Console.
   - Click on 'Your VPCs' on the left-hand side menu.
   - Click on 'Create VPC'.
   - Provide a name for the VPC.
   - Set the IPv4 CIDR block to a /16 block. For example, '10.0.0.0/16'.
   - Leave the IPv6 CIDR block and Tenancy options to their default settings.
   - Check the boxes for 'DNS resolution' and 'DNS hostnames'.
   - Click on 'Create'.

This will create a fully private VPC with no virtual private gateways, internet gateways, transit gateways, or NAT gateways. It will have DNS hostnames and DNS resolution enabled.

Please note that you will need to manually create and configure subnets within this VPC, and ensure that they do not have route tables that direct traffic to a NAT Gateway or Internet Gateway.

### Subnets

### VPC Endpoints
To create the necessary VPC endpoints for a fully private EKS, follow the steps below:

   - Navigate to the VPC Dashboard in the AWS Management Console.
   - Click on 'Endpoints' on the left-hand side menu.
   - Click on 'Create Endpoint'.
   - In the 'Service category' section, select 'AWS services'.
   - In the 'Service Name' dropdown, select the necessary service for your EKS. The required services are:
       - com.amazonaws.region.ec2
       - com.amazonaws.region.ecr.api
       - com.amazonaws.region.ecr.dkr
       - com.amazonaws.region.s3
       - com.amazonaws.region.sts
       - com.amazonaws.region.elasticloadbalancing
       - com.amazonaws.region.ssm
       - com.amazonaws.region.eks
       - com.amazonaws.region.logs
       - com.amazonaws.region.lambda
       - com.amazonaws.region.states
       - com.amazonaws.region.sync-states
       - com.amazonaws.region.cloudformation
       
    - Create an S3 VPC Gateway"
       - com.amazonaws.region.s3
   - In the 'VPC' dropdown, select the VPC you created for your EKS.
   - In the 'Configure route tables' section, select the route tables associated with your VPC.
   - Leave the 'Policy' and 'Private DNS name' to their default settings.
   - Click on 'Create endpoint'.

Repeat these steps for each of the required services. This will create the necessary VPC endpoints for a fully private EKS.
