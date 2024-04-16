
1. How long until app services can really be tested on kubernetes?
2. How will those be deployed, and tested on kubernetes? 
3. We are deploying an app load balancer as part of the setup. what rules need to be configured for the services (if any)?
4. are app services free from high vulnerabilities?

--- 

X 1. postgresql - default database/username? 
    a. IAM role + policies?
    b. what other set ups are needed on the database/objects?

X 2. service ALB rules and configurations - what paths/routes are needed to support the services?

3. How are certificates being managed during your POC? 

4. Is TLS being terminated in current arch? What is the expectation for EKS/Fargate? 

5. Is there anything specific being done with certificates (from app-code side), or can we provide certs to the services without any considerations? 

6. Can we expose secrets to your services via ENVIRONMENT VARIABLES?

7. Pipeline - how are you building and pushing docker images to Artifactory (today)? 

8. For app services (today), are there any vulnerability remediation processes enabled ?

9. post-install steps - 
    1. ask App team how they expect to do this with EKS/Fargate 
    2. ask AWS folks if there's a cleaner approach to deploying sql scripts to RDS after stack deploys

10. service architecture, are routes exposed on the ALB today, /service1, or /service2? is there a singleton api path that all users make?

X 11. how do we minimize the gap between app service team building containers with helm charts that deploy them? who makes / responsible for updating the helm projects?

12. do your services need external DNS addresses, or are internal EKS dns names sufficient for this? externalDNS vs coreDNS
    a. external - creates records on e.g Route53
    b. internal(core) - creates internal records within EKS so services can talk to each other 

13. init container - using base ubuntu image, currently pulls secrets from vault 
14. service image - using base ubuntu image 
15. c++ conversion? binaries 
16. ALB - /* SSL/TLS 
17. how much space does init need on the filesystem to do what it needs to do? they currently use EBS 