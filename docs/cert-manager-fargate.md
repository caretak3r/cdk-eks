## AWS EKS
When using a custom CNI (such as Weave or Calico) on EKS, the webhook cannot be reached by cert-manager. This happens because the control plane cannot be configured to run on a custom CNI on EKS, so the CNIs differ between control plane and worker nodes.

To address this, the webhook can be run in the host network so it can be reached by cert-manager, by setting the webhook.hostNetwork key to true on your deployment, or, if using Helm, configuring it in your values.yaml file.

Note that running on the host network will necessitate changing the webhook's port; see the warning at the top of the page for details.

## AWS Fargate

If you're using AWS Fargate or else if you've specifically configured cert-manager to run the host's network, be aware that kubelet listens on port 10250 by default which clashes with the default port for the cert-manager webhook.

As such, you'll need to change the webhook's port when setting up cert-manager.

**Amend the cert-manager.yaml file to change ports from 10250 to 10260**.


For installations using Helm, you can set the webhook.securePort parameter when installing cert-manager either using a command line flag or an entry in your values.yaml file.

If you have a port clash, you could see confusing error messages regarding untrusted certs. See [#3237](https://github.com/cert-manager/cert-manager/issues/3237) for more details.

