# Kubernetes Controllers

A controller is an implementation of a `control loop pattern` and it's responsibility is to reconcile the desired state, defined by various k8s resources, with the actual state of the system. 

Service controllers watches for new Service resources to be created, and based on the `spec.type`, the controller provisions something using the cloud provider's APIs. 