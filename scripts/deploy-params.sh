#!/bin/bash

cdk deploy \
    --parameters VpcId=vpc-05ad518cb820a49f4 \
    --parameters SubnetIds="subnet-018a105b9762fc5f4,subnet-09be4c2e2e4be3abc,subnet-01358eb54919279c6" \
    --no-previous-parameters \
    --profile default 