# K8s on VMWare

1. VPC requirements 

Most requirements have been eliminated due to the customer bringing their own cluster and configurations. Including the use of VPC endpoints to support a fully isolated cluster. 

2. aws-load-balancer-controller 

Are we allowed to deploy this? Unfamiliar with how k8s hosted on VMware works, but if we need a load balancer, how can this be achieved? If one is provisioned for us already, was it through k8s (does k8s control this ALB)?

Will subnets be tagged properly for auto-discovery to work? 

If ALB is not appropriate for this, or won't work in this customer's environment, how else can this be achieved? Should we implement a virtual load-balancer, or a service mesh with an ingress point being the k8s cluster? 


3. 