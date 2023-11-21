# TODO: add IAM role mapping to the cluster to view it

# self.cluster.add_fargate_profile(
#     "ObservabilityProfile",
#     selectors=[
#         eks.Selector(
#             namespace="observability",
#             labels={"app.kubernetes.io/name": "kubeview"},
#         )
#     ],
# )

# Kubernetes clusters often contain common middleware that has cross-application concerns
# such as observability, certificate management, and more. Such middleware can be easily
# installed with [helm](https://helm.sh/), which is natively supported by the `eks.Cluster` construct.
# In this example, we install KubeView, a visualizer that helps you understand the relationships
# between Kubernetes resources in your cluster.
# (see https://artifacthub.io/packages/helm/kubeview/kubeview)
# self.cluster.add_helm_chart(
#     "KubeView",
#     repository="https://benc-uk.github.io/kubeview/charts",
#     chart="kubeview",
#     namespace="kube-system",
#     values={
#         # control the service name since we will need to
#         # reference to it from our app
#         "fullnameOverride": "kubeview"
#     },
# )
# # Kubeview is exposed via an ELB, and to access it, we need to fetch its generated DNS address.
# # The address is stored in the state of the Kubernetes service that is backed by the ELB, and
# # can be fetched using the `getServiceLoadBalancerAddress` method:
# kube_view_address = self.cluster.get_service_load_balancer_address(
#     "kubeview", namespace="kube-system"
# )
# # We also define a CloudFormation output for this value, so that we can see it once
# # deployment finishes successfully.
# CfnOutput(self, "KubeViewEndpoint", value=f"http://{kube_view_address}")