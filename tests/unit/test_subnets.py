import unittest
from aws_cdk import App, Stack, CfnParameter
from aws_cdk.aws_ec2 import SubnetSelection, Subnet


class TestSubnets(unittest.TestCase):
    def setUp(self):
        self.app = App()
        self.stack = Stack(self.app, "TestStack")
        self.dummy_subnet_ids = "subnet-018a105b9762fc5f4,subnet-09be4c2e2e4be3abc,subnet-01358eb54919279c6"

    def test_subnet_ids(self):
        subnet_ids = self.dummy_subnet_ids.split(",")
        vpc_subnets = SubnetSelection(
            subnets=[
                Subnet.from_subnet_id(self.stack, f"Subnet{i}", subnet_id)
                for i, subnet_id in enumerate(subnet_ids)
            ]
        )
        self.assertIsInstance(vpc_subnets, SubnetSelection)

    def test_subnet_ids_cfnparameter(self):
        pass


if __name__ == "__main__":
    unittest.main()
