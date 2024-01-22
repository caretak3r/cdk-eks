# Viewing EKS Resources 

Since we use federated IAM SSO Roles, we get errors when trying to add this role to the masters group. This document will show you what to do, to circumvent adding this role manually to the cluster. 

1. In `lib/constants.py` find the variable `AUTHORIZED_ROLE_LIST`.

2. Add any number of IAM Roles as a list, e.g `AUTHORIZED_ROLE_LIST = ["arn::1", "arn::2"]`.

3. When `stacks/eks_stack.py` gets deployed, a function called `add_to_masters_role` will add these roles to the cluster. 

4. Once that's completed, in the AWS Console you must `Switch Role`.

5. Use the ACCOUNT_ID, use an IAM Role that was added in step 2, and Switch Roles. 

6. That IAM role should now be able to view resources in EKS. 