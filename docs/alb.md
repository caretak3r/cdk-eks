# ALB

## This ONLY WORKS if VPC has a route to the public internet. Otherwise we deploy the ALB controller manually.

In order to access applications inside the clusters from the internet, the cluster needs the ability to provision on-demand AWS load balancers that route to internal Kubernetes resources. (see https://github.com/aws/aws-cdk/tree/main/packages/aws-cdk-lib/aws-eks#alb-controller)

    alb_controller=eks.AlbControllerOptions(
        version=eks.AlbControllerVersion.V2_5_4
    ),  # Deploy the ALB controller to the cluster

## Creating the ingress

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

## On Fargate

The AWS Load Balancer Controller supports the following traffic modes:

Instance – Registers nodes within your cluster as targets for the ALB. Traffic reaching the ALB is routed to NodePort for your service and then proxied to your Pods. This is the default traffic mode. You can also explicitly specify it with the alb.ingress.kubernetes.io/target-type: instance annotation.

Note
Your Kubernetes service must specify the NodePort or "LoadBalancer" type to use this traffic mode.

IP – Registers Pods as targets for the ALB. Traffic reaching the ALB is directly routed to Pods for your service. You must specify the `alb.ingress.kubernetes.io/target-type: ip` annotation to use this traffic mode. The IP target type is required when target Pods are running on Fargate.