# 1. create or provide a KMS key

# 2. shuffle tables - downloads secrets (data encryption keys) -> generate shuffle tables -> encrypt with data key -> upload to s3
# 2a.-> if no secrets -> generate -> push to secrets manager 
# 2b. --> encrypt with data key? 

# 3. service starts up -> gets those secrets SSM (from step 2)

# services will need KMS and SecretsManager IAM policies attached to FargateWorkers 

# 