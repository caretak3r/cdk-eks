curl -L https://istio.io/downloadIstio | ISTIO_VERSION=1.11.0 sh -
cd istio-1.11.0
export PATH=$PWD/bin:$PATH
```

### Deploying Istio Using the Istio Operator

Deploy the Istio Operator, which will manage the Istio service mesh:

```yaml
kubectl apply -f manifests/charts/istio-operator/
```

Deploy Istio using the operator:

```yaml
kubectl create ns istio-system
kubectl apply -n istio-system -f - <<EOF
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
spec:
  profile: demo
EOF
```

### Verifying Installation

Verify that Istio has been installed correctly:

```bash
kubectl get pods -n istio-system
```

## Configuring mTLS in Istio

Enforce strict mTLS across the service mesh:

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT
```

## Setting Up Istio Ingress Gateway

Integrate Istio with AWS Load Balancer:

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: istio-ingressgateway
  namespace: istio-system
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "*"
```

## Defining Access Control Policies

Restrict access using Istio `AuthorizationPolicies`:

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: restrict-access
  namespace: istio-system
spec:
  selector:
    matchLabels:
      app: myapp
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/myapp-service-account"]
