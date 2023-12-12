# Telemetry

We should also install container insights: 

```
# Add container insight (CloudWatch Log) to EKS
KubernetesManifest(self,'ContainerInsight',
    cluster=eks_cluster, 
    manifest=load_yaml_replace_var_remotely('https://raw.githubusercontent.com/aws-samples/amazon-cloudwatch-container-insights/latest/k8s-deployment-manifest-templates/deployment-mode/daemonset/container-insights-monitoring/quickstart/cwagent-fluentd-quickstart.yaml', 
            fields=_var_mapping,
            multi_resource=True
    )
)
```