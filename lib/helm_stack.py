from aws_cdk import (
    aws_eks as eks,
    aws_ecr as ecr,
    core,
)

class HelmStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, eks_cluster, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Pull helm chart from ECR repository
        ecr_repository = ecr.Repository.from_repository_name(self, "EcrRepo", "my_ecr_repo")

        # Deploy Helm chart to the EKS cluster
        eks.HelmChart(self, "MyHelmChart",
            cluster=eks_cluster,  # existing EKS cluster
            chart="my_chart",  # name of the Helm chart
            repository=ecr_repository.repository_uri,  # ECR repository URI
            namespace="default",  # Kubernetes namespace to deploy into
            version="1.0.0",   # Helm chart version
            values={"key": "value"}  # values to pass to the Helm chart
        )

app = core.App()
HelmStack(app, "HelmStack")
app.synth()
