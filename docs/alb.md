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