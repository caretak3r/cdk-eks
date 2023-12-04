# ALB - AWS Load Balancer Controller for EKS

## CDK
### This ONLY WORKS if VPC has a route to the public internet. Otherwise we deploy the ALB controller manually.

In order to access applications inside the clusters from the internet, the cluster needs the ability to provision on-demand AWS load balancers that route to internal Kubernetes resources. (see https://github.com/aws/aws-cdk/tree/main/packages/aws-cdk-lib/aws-eks#alb-controller)

    alb_controller=eks.AlbControllerOptions(
        version=eks.AlbControllerVersion.V2_5_4
    ),  # Deploy the ALB controller to the cluster

---

## Fargate Considerations

The AWS Load Balancer Controller supports the following traffic modes:

Instance – Registers nodes within your cluster as targets for the ALB. Traffic reaching the ALB is routed to NodePort for your service and then proxied to your Pods. This is the default traffic mode. You can also explicitly specify it with the alb.ingress.kubernetes.io/target-type: instance annotation.

Note
Your Kubernetes service must specify the NodePort or "LoadBalancer" type to use this traffic mode.

IP – Registers Pods as targets for the ALB. Traffic reaching the ALB is directly routed to Pods for your service. You must specify the `alb.ingress.kubernetes.io/target-type: ip` annotation to use this traffic mode. **The IP target type is required when target Pods are running on Fargate.**

---

## Ingress

Ingress is a resource type that provides access to Pods behind Services. 

For Ingress objects, it’s the responsibility of an Ingress controller to create the necessary wiring, provision the load balancing component, and reconcile the state of the cluster. AWS EKS provides a supported controller via the AWS Load Balancer Controller, but it still must be installed.

The AWS implementation for Ingress controller, AWS Load Balancer Controller, translates the Ingress rules, parameters, and annotations into the Application Load Balancer configuration, creating listeners and target groups and connecting their targets to the backend Services.

```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: some-ingress
    annotations:     
      alb.ingress.kubernetes.io/load-balancer-name: ingress
      alb.ingress.kubernetes.io/target-type: ip
      alb.ingress.kubernetes.io/scheme: internet-facing
spec:
  ingressClassName: alb
  rules:
    - host: my.example.com
      http:
        paths:
          - path: /some-path
            pathType: Prefix
            backend:
              service:
                name: service-a
                port:
                  number: 80
          - path: /some-other-path
            pathType: Exact
            backend:
              service:
                name: service-b
                port:
                  number: 81
```

## Services: Creating the ingress

Something like this can be used to apply the annotations to create an ingress on the ALB: 

```
---
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  namespace: game-2048
  name: ingress-2048
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
spec:
  rules:
    - http:
        paths:
          - path: /*
            backend:
              serviceName: service-2048
              servicePort: 80
```

## Ingress: Internal Reverse Proxy
![Alt text](image-5.png)

In this case, the implementation is delegated to an internal, in-cluster Layer 7 reverse proxy (e.g., NGINX), that receives the traffic from outside the cluster and routes it to the backend Services based on Ingress configuration.

![Alt text](image-6.png)

In the diagram below, we see the step-by-step process of exposing an application behind an Ingress:

1. The alb-ingress-controller watches for Ingress events.
2. An ALB is managed for each Ingress object. It is created, configured, and deleted as required.
3. Target groups are created, with instance (ServiceA and ServiceB) or ip (ServiceC) modes.
4. The ALB listeners are created and configured.
5. Rules are configured to forward traffic from the listeners to the target groups.