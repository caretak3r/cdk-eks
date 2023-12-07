# dependencies 

Application teams are deploying services to Kubernetes for the first time. Some things need to be considered. 


## Application - Helm

1. Helm chart configurations are needed from application teams. 
    - mimic what configurations apps are using right now
    - add base helm templates
    - init container considerations
    - actual service container considerations


## Application - Scaling
1. What configurations should be used to deploy service to Fargate? 
    - performance testing _should_ give us benchmarks to use for customer deployment


## Application - Certificates 
We will use cert-manager to distribute certificates to the pods based on the certificate the customer provides. 

1. Are the services currently packaging certificates during the docker build? 


## Installer - Progress
1. We have the aws load balancing + ingress functionality working. Only thing left is to test using this in conjunction with cert-manager for certificate issuance.
2. We are currently working on configuring cert-manager properly with AWS Private CA, since it doesn't support ACM.
3. We are currently working on secrets-operator, doing a POC to see how we can manage secrets in various secrets management systems (e.g AWS Secrets Manager, Vault, etc).
4. We deployed a sample service with a simple docker build using helm. We built this from scratch. 

## Installer - Infra Validations (pre-install)
1. We need to check if the VPC, Subnets and Route Tables are configured properly. 
    a. Check if VPC has enableDNSHostname and DNS support enabled. 
    b. Check if Subnets have minimum IP addresses. 
    c. Check if Subnets have been tagged properly. 
    d. Check if VPC Endpoints have been created. 
    e. Check if VPC Endpoints have a "permissive" security group to allow traffic from VPC. 
    f. Check if ECR and artifacts have been shared and are available. 
    g. 

## Installer - Infra Validations (post-install)
1. We need to test that the RDS database is accessible with managed secrets from the cluster. 
2. We need to test that the S3 bucket is accessible, and writable. 
3. We need to check that AWS Load Balancer Controller pods are up and running.
4. We need to check that cert-manager pods are up and running.
5. We need to check that secrets-operator pods are up and running. 
6. We need to check that basic log groups are being created by fluent-bit in CloudWatch.
7. Once all services have been deployed and confirmed in good state, we need to test the endpoint we are exposing.
8. We need to use tools to run "smoke tests" quickly to confirm things.

