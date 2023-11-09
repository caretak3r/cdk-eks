AWS_ACCOUNT=$(shell aws sts get-caller-identity | jq -r '.Account')
AWS_REGION=$(shell aws configure get region)

CUSTOMER_VPC_ID?=vpc-0PLACEHOLDER000004
CUSTOMER_SUBNET_IDS?=subnet-0PLACEHOLDER000009,subnet-0PLACEHOLDER000010,subnet-0PLACEHOLDER000011


synth:
	export AWS_ACCOUNT=$(AWS_ACCOUNT) AWS_REGION=$(AWS_REGION) && cdk synth --parameters VpcId=$(CUSTOMER_VPC_ID) --parameters SubnetIds=$(CUSTOMER_SUBNET_IDS)

deploy-py:
	export AWS_ACCOUNT=$(AWS_ACCOUNT) AWS_REGION=$(AWS_REGION) && cdk deploy --app="python app.py" --require-approval=never --no-previous-parameters --parameters VpcId=$(CUSTOMER_VPC_ID) --parameters SubnetIds=$(CUSTOMER_SUBNET_IDS)

deploy-all:
	export AWS_ACCOUNT=$(AWS_ACCOUNT) AWS_REGION=$(AWS_REGION) && cdk deploy --all --require-approval=never --no-previous-parameters --parameters VpcId=$(CUSTOMER_VPC_ID) --parameters SubnetIds=$(CUSTOMER_SUBNET_IDS)

deploy:
	cdk deploy --all --require-approval=never --no-previous-parameters

docker-compose-build:
	docker-compose build

docker-compose-up:
	docker-compose up -d