#!make
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

# build: this just builds the docker image locally
builds:
	docker build -t tkp-cdk .

# shell: this brings up the docker container and drops you into a shell
shell:
	docker run -v ${HOME}/.aws:/home/cdk/.aws -v ${PWD}:/app --env-file .env -it tkp-cdk /bin/sh

# d-bootstrap: this runs the cdk bootstrap command - no shell required just use the existing container to run the command
d-bootstrap:
	docker run -v ${HOME}/.aws:/home/cdk/.aws --env-file .env -it tkp-cdk cdk bootstrap

# bootstrap: this runs the cdk bootstrap command within the container
bootstrap:
	cdk bootstrap

# d-synth: this runs the cdk synth command from the host
d-synth:
	docker run -v ${HOME}/.aws:/home/cdk/.aws --env-file .env -it tkp-cdk cdk synth

synth:
	cdk synth

# deploy: this runs the cdk deploy command
d-deploy:
	docker run -v ${HOME}/.aws:/home/cdk/.aws --env-file .env -it tkp-cdk cdk deploy --require-approval=never --no-previous-parameters

deploy:
	cdk deploy --require-approval=never --no-previous-parameters --no-rollback

# this should check if local aws credentials and config files exist, and region and account ids can be retrieved by running aws sts get-caller-identity
# FIXME: this doesn't work yet
check:
	@echo "Checking for AWS credentials and config files..."
	@if [ -f ${HOME}/.aws/credentials ]; then \
		echo "AWS credentials file found."; \
	else \
		echo -e "\e[31mAWS credentials file NOT found.\e[0m"; \
	fi
	@if [ -f ${HOME}/.aws/config ]; then \
		echo "AWS config file found."; \
	else \
		echo -e "\e[31mAWS config file NOT found.\e[0m"; \
	fi
	@if [ -z "$${AWS_ACCESS_KEY_ID}" ]; then \
		echo -e "\e[31mAWS_ACCESS_KEY_ID is NOT set.\e[0m"; \
	else \
		echo "AWS_ACCESS_KEY_ID is set."; \
	fi
	@if [ -z "$${AWS_SECRET_ACCESS_KEY}" ]; then \
		echo -e "\e[31mAWS_SECRET_ACCESS_KEY is NOT set.\e[0m"; \
	else \
		echo "AWS_SECRET_ACCESS_KEY is set."; \
	fi
	@if [ -z "$${AWS_SESSION_TOKEN}" ]; then \
		echo -e "\e[31mAWS_SESSION_TOKEN is NOT set.\e[0m"; \
	else \
		echo "AWS_SESSION_TOKEN is set."; \
	fi
	@echo "Checking for AWS region..."
	@AWS_REGION=$$(aws configure get region); \
	if [ -z "$$AWS_REGION" ]; then \
		echo -e "\e[31mAWS region NOT found.\e[0m"; \
	else \
		echo "AWS region is $$AWS_REGION."; \
	fi
	@echo "Checking for AWS account id..."
	@AWS_ACCOUNT_ID=$$(aws sts get-caller-identity --query Account --output text); \
	if [ -z "$$AWS_ACCOUNT_ID" ]; then \
		echo -e "\e[31mAWS account id NOT found.\e[0m"; \
	else \
		echo "AWS account id is $$AWS_ACCOUNT_ID."; \
	fi


install:
	@echo "Checking for AWS credentials and config files..."
	make check
	@echo "Bootstrapping environment"
	make bootstrap
	@echo "Deploying environment stack"
	make deploy

.PHONY: builds shell bootstrap synth deploy check install