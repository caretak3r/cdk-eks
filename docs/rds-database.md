# Creating a new database + users for RDS

## Option 1: Run SQL scripts with a CustomResource and Lambda

This would require also creating a CustomResource and a Lambda that will run the SQL scripts to create a new database and/or new users. After the RDS stack is deployed, the CustomResource invokes the Lambda, which then connects to the instance using the admin credentials to run the SQL scripts. 

- [Use AWS CDK to initialize Amazon RDS instances (in ts)](https://aws.amazon.com/blogs/infrastructure-and-automation/use-aws-cdk-to-initialize-amazon-rds-instances/)
  - Looks like this is provisioning resources with CDK and then using the Lambda + SDK to run the SQL script
- [DDL Deployment for Amazon RDS (also in ts)](https://github.com/aws-samples/ddl-deployment-for-amazon-rds/blob/main/README.md)
  - This example uses Aurora Serverless v1 (PostgreSQL) to access the RDS Data API, but looks like using CustomResources is also an option if using a different configuration - would use something like [psycopg2](https://pypi.org/project/psycopg2/) on the Lambda
  - SQL script gets uploaded to S3 bucket, Lambda pulls script from bucket and executes on the database
  - Resources (Likely Lambda + CustomResource for our case) provisioned using CDK, Lambda uses Python SDK to execute the script


## Option 2: Run SQL scripts w/o adding additional resources, using SDK/Psycopg

SDK has a function under RDSDataService called [execute_statement](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds-data/client/execute_statement.html) that can be used to run SQL statements. Not 100% sure if we can use this, but if we can, we could use this to run the statements after connecting to the database.

Another option is following along with what's mentioned [here](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/UsingWithRDS.IAMDBAuth.Connecting.Python.html) to connect and execute SQL scripts on a cluster.

After the RDS stack is deployed, connect to the instance and run the SQL scripts to create the databases and users. This doesn't require creating additional resources in AWS. 