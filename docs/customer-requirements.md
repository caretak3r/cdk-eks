# Customer Requirements

We support the creation of fully-private clusters that have no outbound internet access and have only private subnets. VPC endpoints are used to enable private access to AWS services.

This guide describes how to create a "zero-trust" networking environment in AWS. 


## Table of Contents
0. [IAM Permissions](#iam-permissions)
1. [Artifacts and Elastic Container Repository (ECR)](#artifacts-and-elastic-container-repository-ecr)
2. [AWS Network Setup](#aws-network-setup)

   a. [Private Virtual Private Cloud (VPC)](#private-virtual-private-cloud-vpc)

   b. [Subnets](#subnets)

   c. [Route Tables](#route-tables)

   d. [VPC Endpoints](#vpc-endpoints)

3. [CloudFormation](#cloudformation)

   a. [Network](#network)

   b. [Infrastructure](#infrastructure)

   c. [Product](#product)

---


## IAM Permissions

In order to deploy the cdk project certain IAM permissions are required by the operator and CloudFormation stacks to complete provisioning of the infrastructure and product setup. 

Here is the least priviledged IAM policy that should be created prior to executing any deployments. 

```
<insert IAM policy here>
```
---

## Artifacts and Elastic Container Repository (ECR)

---

## AWS Network Setup

### Private Virtual Private Cloud (VPC)

This will create a fully private VPC with no virtual private gateways, internet gateways, transit gateways, or NAT gateways. It will have DNS hostnames and DNS resolution enabled.

Please note that you will need to manually create and configure subnets within this VPC, and ensure that they do not have route tables that direct traffic to a NAT Gateway or Internet Gateway, as this is a **fully private solution**. 

### Subnets

**Private subnets** – Must be tagged in the following format. This is so that Kubernetes and the AWS load balancer controller know that the subnets can be used for internal load balancers. If you use eksctl or an Amazon EKS AWS CloudFormation template to create your VPC after March 26, 2020, the subnets are tagged appropriately when created.

    Key – kubernetes.io/role/internal-elb
    Value – 1

### Route Tables

Since this is a fully private network setup, the only routes that will be needed are the following:

| Destination | Target | 
| --- | --- | 
| `VPC CIDR RANGE` | local |
| `pl-XXXXXXXX` | `vpce-s3-gateway` | 

In this setup, we have the entire VPC CIDR Range routing to `local` and the prefix list (indicated by the `pl-`) routing to the S3 Gateway Endpoint that will be created in the next section. This should automatically be done for you, once the S3 Gateway Endpoint is provisioned, and the correct subnets are selected.


### VPC Endpoints
To create the necessary VPC endpoints for a fully private EKS, follow the steps below:

   1. Create a security group that allows the resources in your VPC to communicate with the endpoint network interfaces for the VPC endpoint. To ensure that tools such as the `AWS CLI`, `kubectl`, and `helm` can make requests over HTTPS from resources in the VPC to the AWS service, the security group must allow inbound HTTPS traffic.

      > If your resources are in a subnet with a network ACL, verify that the network ACL allows traffic between the endpoint network interfaces and the resources in the VPC.

      _The minimal rules for a security group looks like this:_
      | Name | IP Version | Type | Protocol | Port Range | Destination |
      | --- | --- | --- | --- | --- | --- |
      | Inbound | IPv4 | All traffic | All | All | 0.0.0.0/0 | 
      | Outbound | IPv4 | All traffic| All | All | 0.0.0.0/0 |

   2. Create a VPC endpoint for each of the following services:

      | Service Name | VPC Endpoint |
      | --- | --- |
      | EC2 | com.amazonaws.region.ec2 |
      | ECR API | com.amazonaws.region.ecr.api |
      | ECR DKR | com.amazonaws.region.ecr.dkr |
      | STS | com.amazonaws.region.sts |
      | Elastic Load Balancing | com.amazonaws.region.elasticloadbalancing |
      | SSM | com.amazonaws.region.ssm |
      | EKS | com.amazonaws.region.eks |
      | CloudWatch Logs | com.amazonaws.region.logs |
      | Lambda | com.amazonaws.region.lambda |
      | Step Functions | com.amazonaws.region.states |
      | Sync States | com.amazonaws.region.sync-states |
      | CloudFormation | com.amazonaws.region.cloudformation |
      | S3 | com.amazonaws.region.s3 |

   3. For each service, follow these steps:
      1. Navigate to the VPC Dashboard in the AWS Management Console.
      2. Click on 'Endpoints' on the left-hand side menu.
      3. Click on 'Create Endpoint'.
      4. In the 'Service category' section, select 'AWS services'.
      5. In the 'Service Name' dropdown, select the necessary service for your EKS. The required services are:

         `- com.amazonaws.region.ec2`
         
         `- com.amazonaws.region.ecr.api`
         
         `- com.amazonaws.region.ecr.dkr`
         
         `- com.amazonaws.region.sts`

         `- com.amazonaws.region.elasticloadbalancing`
         
         `- com.amazonaws.region.ssm`

         `- com.amazonaws.region.eks`
         
         `- com.amazonaws.region.logs`
         
         `- com.amazonaws.region.lambda`

         `- com.amazonaws.region.states`

         `- com.amazonaws.region.sync-states`

         `- com.amazonaws.region.cloudformation`

   4. Create an S3 VPC Gateway
      1. In the 'VPC' dropdown, select the VPC you created for the product deployment.
      2. In the 'Configure route tables' section, select the route tables associated with your VPC.
      3. Leave the 'Policy' and 'Private DNS name' to their default settings.
      4. Click on 'Create endpoint'.

         `- com.amazonaws.region.s3`
      
   5. Each of the VPC endpoints above should be created using the **private subnets** that were created and tagged in the previous section. Associate both subnets to each of the VPC endpoints, and use a security group

   
Repeat these steps for each of the required services. This will create the necessary VPC endpoints for a fully private EKS.
