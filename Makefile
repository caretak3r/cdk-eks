#!make
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

# build: this just builds the docker image locally
builds:
	docker build -t tkp-cdk-dev .

# dev 
dev:
	docker build -t tkp-cdk-dev .
	docker run -v ${HOME}/.aws:/home/cdk/.aws -v ${PWD}:/app -it tkp-cdk-dev

# shell: this brings up the docker container and drops you into a shell
shell:
	docker run -v ${HOME}/.aws:/home/cdk/.aws -v ${PWD}:/app --env-file .env -it tkp-cdk-dev /bin/sh

# bootstrap: this runs the cdk bootstrap command within the container
bootstrap:
	cdk bootstrap --termination-protection=true --toolkit-stack-name platform-cdk-toolkit --qualifier pg --tags "managed_by=platform-cdk" --debug --verbose

synth:
	cdk synth

# deploy: this runs the cdk deploy command
deploy:
	cdk deploy * --require-approval=never --no-previous-parameters --verbose --debug --no-rollback

.PHONY: builds shell bootstrap synth deploy