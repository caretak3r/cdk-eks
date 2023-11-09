#!/bin/bash

cdk deploy \
    --context VpcId=vpc-0PLACEHOLDER000004 \
    --context SubnetIds="subnet-0PLACEHOLDER000009,subnet-0PLACEHOLDER000010,subnet-0PLACEHOLDER000011" \
    --no-previous-parameters \
    --profile default 


cdk deploy --context VpcId=vpc-0PLACEHOLDER000004 --context SubnetIds="subnet-0PLACEHOLDER000009,subnet-0PLACEHOLDER000010,subnet-0PLACEHOLDER000011" --no-previous-parameters