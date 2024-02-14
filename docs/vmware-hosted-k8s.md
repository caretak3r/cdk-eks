# K8s on VMWare

1. VPC requirements 

Most requirements have been eliminated due to the customer bringing their own cluster and configurations. Including the use of VPC endpoints to support a fully isolated cluster. 

2. aws-load-balancer-controller 

Are we allowed to deploy this? Unfamiliar with how k8s hosted on VMware works, but if we need a load balancer, how can this be achieved? If one is provisioned for us already, was it through k8s (does k8s control this ALB)?

Will subnets be tagged properly for auto-discovery to work? 

If ALB is not appropriate for this, or won't work in this customer's environment, how else can this be achieved? Should we implement a virtual load-balancer, or a service mesh with an ingress point being the k8s cluster? 


3. cert-manager

Is the customer going to provide the certificates? 

We understand the customer will provide the load-balancer certificate (if ALB is even in play here, not sure, look at #aws-load-balancer-controller).

We're still in the same spot where the intermediate certificates or bundles for the applications cannot be generated without the use of private CA or some other mechanism. Considering the customer environment, it's probable that the customer might already have Certificates in kubernetes already provisioned and ready to be used. In which case, our helm deployments should account for this need. 

4. Vault 

What vault version is the customer using? v1 and v2 differences exist, and effects our ability to set up secrets-service, unless we had a flag to use v1 or v2. 

5. 