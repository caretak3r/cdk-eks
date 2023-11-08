import unittest
from aws_cdk import App, Stack, CfnParameter
from aws_cdk.aws_ec2 import SubnetSelection, Subnet


class TestSubnets(unittest.TestCase):
    def setUp(self):
        self.app = App()
        self.stack = Stack(self.app, "TestStack")
        self.dummy_subnet_ids = "subnet-0PLACEHOLDER000009,subnet-0PLACEHOLDER000010,subnet-0PLACEHOLDER000011"

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
