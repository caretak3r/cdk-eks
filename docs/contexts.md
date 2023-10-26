        # vpc_id = self.node.try_get_context("VpcId") or None
        # print(f"CONTEXT vpc_id: {vpc_id}")

        # subnetIds = self.node.try_get_context("SubnetIds") or None
        # print(f"CONTEXT subnetIds: {subnetIds}")

        vpc = vpc_id_param.value_as_string
        print(f"vpc: {vpc}")
        
        subnet_ids = subnet_ids_param.value_as_list
        print(f"subnet_ids: {subnet_ids}")

        vpc_subnets = ec2.SubnetSelection(
            subnets=[
                ec2.Subnet.from_subnet_id(self, f"Subnet{i}", subnet_id)
                for i, subnet_id in enumerate(subnet_ids)
            ]
        )