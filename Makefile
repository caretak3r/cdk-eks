#!make
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

# build: this just builds the docker image locally
builds:
	docker build -t tkp-cdk .

# dev 
dev:
	docker build -t tkp-cdk-dev -f Dockerfile.dev .
	docker run -v ${HOME}/.aws:/home/cdk/.aws -v ${PWD}:/app -it tkp-cdk-dev

# shell: this brings up the docker container and drops you into a shell
shell:
	docker run -v ${HOME}/.aws:/home/cdk/.aws -v ${PWD}:/app --env-file .env -it tkp-cdk /bin/sh

# d-bootstrap: this runs the cdk bootstrap command - no shell required just use the existing container to run the command
d-bootstrap:
	docker run -v ${HOME}/.aws:/home/cdk/.aws --env-file .env -it tkp-cdk cdk bootstrap

# bootstrap: this runs the cdk bootstrap command within the container
#TODO: add termination protection and tags to the bootstrap command (already a default)
bootstrap:
	cdk bootstrap --toolkit-stack-name tkp-cdk-toolkit

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

.PHONY: builds shell bootstrap synth deploy