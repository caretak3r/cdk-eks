from aws_cdk import aws_ec2 as ec2, aws_route53 as r53, core


class VaultStack(core.Stack):
    def __init__(
        self, scope: core.Construct, id: str, hosted_zone: str, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a security group
        sg = ec2.SecurityGroup(
            self,
            "VaultSG",
            vpc=ec2.Vpc.from_lookup(self, "DefaultVPC", is_default=True),
            description="Allow ssh access to ec2 instances",
            allow_all_outbound=True,
        )
        sg.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "allow ssh access from the world"
        )
        sg.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(8200), "allow vault access from the world"
        )

        # Define the user data script
        user_data_script = """#!/bin/bash
        sudo apt-get update -y
        sudo apt-get install -y curl unzip jq
        curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
        sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
        sudo apt-get update && sudo apt-get install vault
        sudo systemctl enable vault
        sudo systemctl start vault
        """

        # Create an EC2 instance
        instance = ec2.Instance(
            self,
            "VaultInstance",
            instance_type=ec2.InstanceType("m4.large"),
            machine_image=ec2.MachineImage.latest_amazon_linux(),
            vpc=ec2.Vpc.from_lookup(self, "DefaultVPC", is_default=True),
            security_group=sg,
            user_data=ec2.UserData.custom(user_data_script),
        )

        # Create a Route53 record
        r53.ARecord(
            self,
            "VaultDNS",
            zone=r53.HostedZone.from_lookup(
                self, "HostedZone", domain_name=hosted_zone
            ),
            record_name="vault",
            target=r53.RecordTarget.from_ip_addresses(instance.instance_public_ip),
        )
