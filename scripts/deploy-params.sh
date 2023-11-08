#!/bin/bash

cdk deploy \
    --parameters VpcId=vpc-0PLACEHOLDER000004 \
    --parameters SubnetIds="subnet-0PLACEHOLDER000009,subnet-0PLACEHOLDER000010,subnet-0PLACEHOLDER000011" \
    --no-previous-parameters \
    --profile default 