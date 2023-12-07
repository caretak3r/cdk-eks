import constants
from aws_cdk import (
    aws_iam as iam,
)


def enable_ec2_masters_role(self):
    # IAM: Add IAM roles from constants to the `system:masters` group
    # TODO: how will this work in a customer environment? Do we assign the operator's role to the cluster?
    # FIXME: this runs successfully the first time, but fails on subsequent runs - kubectl apply AlreadyExists error
    for role in constants.AUTHORIZED_ROLE_LIST:
        auth_role = iam.Role.from_role_arn(
            self, f"ImportedIAMRole{role.split('/')[-1]}", role
        )
        # self.cluster.aws_auth.add_role_mapping(auth_role, groups=["system:masters"])
        self.cluster.aws_auth.add_masters_role(auth_role)

        self.cluster.add_manifest(
            f"AdminRoleManifest{role.split('/')[-1]}",
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRoleBinding",
                "metadata": {"name": "admin-role-binding"},
                "roleRef": {
                    "apiGroup": "rbac.authorization.k8s.io",
                    "kind": "ClusterRole",
                    "name": "cluster-admin",
                },
                "subjects": [
                    {
                        "kind": "ServiceAccount",
                        "name": auth_role.role_name,
                        "namespace": "kube-system",
                    }
                ],
            },
        )
