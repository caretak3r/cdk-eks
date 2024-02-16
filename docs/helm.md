# Helm

There will be some helm packages that will need to be maintained, built repeatedly, and distributed to our OCI registries. 

1. aws-load-balancer-controller (daemonset)
2. cert-manager (daemonset)
3. manchester-secrets-service-broker (sidecar container)
4. manchester-init (init container)
5. manchester-main 
6. manchester-db-init (init container)
7. karpenter (daemonset)
8. fluent-bit (daemonset)
9. otel-collector (daemonset)
10. metrics-server (daemonset)

Optional: 

1. hashicorp vault

---

## Init Containers

We specifically use init-containers in order to do some preparation work such as database initializations, and application-specific steps. These containers **MUST** complete successfully before proceeding to the next deployments, due to the requires the application has. 

### Why Do We Use Init Containers?

Setup Tasks: Init containers can do tasks like downloading important files, preparing databases, or fetching secret information.

Dependencies: Sometimes, your app needs other services to be ready, like a database. Init containers ensure these dependencies are in place before your app starts.

Delaying Start: You might want to wait for something to be ready, like an external service. Init containers help delay your app’s start until it’s the right time.

If you specify multiple init containers for a Pod, kubelet runs each init container sequentially. Each init container must succeed before the next can run. When all of the init containers have run to completion, kubelet initializes the application containers for the Pod and runs them as usual.

When it comes to **Kubernetes Jobs** however, jobs are utilized for executing batch processes that complete their run, while Init Containers are employed to perform a specific task before the main container is launched. **Init Containers are a part of the Pod's lifecycle, whereas K8s Jobs creates a new pod for each execution.**

### Common Scenarios for Init Containers:

Database Setup: Imagine you have a website that requires a database to store user information. You can use an Init container to make sure the database is set up and ready before your website starts running.

Fetching Configurations: Your app might need settings or configurations from outside sources. Init containers can fetch these for your app.

Waiting for Services: If your app relies on another service, like an external database, an init container can wait until that service is ready.

Scenario: You have a web application that relies on a database. Before your web application starts, you want to ensure the database is initialized and ready to accept connections.

---

## Sidecar Containers 

### Why Do We Use Sidecar Containers?

Sidecar containers are utility containers in a pod that help the main application to do its job. They are part of the same pod as the main application and share the same lifecycle and resources. 

Here are some reasons why we use sidecar containers:

1. **Separation of Concerns**: Sidecar containers allow us to separate the logic of our main application from the auxiliary tasks that support the application. This makes our main application simpler and easier to maintain.

2. **Reusability**: Sidecar containers can be reused across different applications. For example, a sidecar container that handles logging or monitoring can be used with any application.

3. **Scalability**: Sidecar containers can be scaled independently from the main application. This is useful when the load on the sidecar container is different from the load on the main application.

In our case, we are using a sidecar container for the `manchester-secrets-service-broker`. This sidecar container handles the task of managing secrets, which is a supporting task that is separate from the main functionality of the application. By using a sidecar container, we can keep the logic for managing secrets separate from the main application, making the main application simpler and easier to maintain.

---

## Helm Umbrella Projects

A Helm Umbrella project is a Helm chart that has dependencies on other Helm charts. It is a way to manage deployments of multiple Helm charts from a single parent chart. The parent chart is often referred to as the "umbrella" chart, and the charts it depends on are its subcharts.

The umbrella chart's `Chart.yaml` file includes a `dependencies` section where you specify each dependent chart (subchart). The umbrella chart's `values.yaml` file can then be used to manage the configurations for all of its subcharts.

### Why Do We Use Helm Umbrella Projects?

There are several reasons why we use Helm umbrella projects:

1. **Simplicity**: It simplifies the deployment process. Instead of having to manage multiple individual Helm charts, you can manage them all from a single umbrella chart.

2. **Consistency**: It ensures consistency across deployments. By managing all of your charts from a single umbrella chart, you can ensure that they all use the same configurations.

3. **Reusability**: It promotes reusability. You can use the same subchart in multiple umbrella charts.

4. **Isolation**: It provides isolation. Changes to one subchart do not affect other subcharts unless they are explicitly configured to do so.

In the context of the projects listed in the directory, each project (like `aws-load-balancer-controller`, `cert-manager`, `secrets-service-broker`, etc.) can be managed as a subchart under an umbrella chart. This allows us to manage all these projects from a single place, ensuring consistency and simplicity in our deployments.


---
## Directory

| Package Name | Helm Repository | Docker Image | Purpose |
|--------------|-----------------|--------------|---------|
| aws-load-balancer-controller | | | | 
| cert-manager | | | | 
| secrets-service-broker | | | | 
| tokenapp-init | | | | 
| tokenapp-main | | | | 
| tokenapp-db-init | | | | 
| karpenter | | | |
| fluent-bit | | | | 
| otel-collector | | | | 
| metrics-server | | | | 
| vault | | | | Optional |
