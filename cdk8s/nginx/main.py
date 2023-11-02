from constructs import Construct
from cdk8s import App, Chart
from imports import k8s
import cdk8s_plus as kplus


class Nginx(Chart):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        label = {"app": "nginx"}

        k8s.KubeDeployment(
            self,
            "nginx-deployment",
            spec=k8s.DeploymentSpec(
                replicas=1,
                selector=k8s.LabelSelector(match_labels=label),
                template=k8s.PodTemplateSpec(
                    metadata=k8s.ObjectMeta(labels=label),
                    spec=k8s.PodSpec(
                        containers=[
                            k8s.Container(
                                name="nginx",
                                image="nginx:latest",
                                ports=[k8s.ContainerPort(container_port=8080)],
                            )
                        ]
                    ),
                ),
            ),
        )

        k8s.KubeService(
            self,
            "service",
            spec=k8s.ServiceSpec(
                type="LoadBalancer",
                ports=[
                    k8s.ServicePort(
                        port=80, target_port=k8s.IntOrString.from_number(8080)
                    )
                ],
                selector=label,
            ),
        )


app = App()
Nginx(app, "nginx")

app.synth()
