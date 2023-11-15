# TODO: have the python and alpine packages already installed in the image
ARG ALPINE_VERSION=3.18
FROM alpine:${ALPINE_VERSION}

ARG AWS_CDK_VERSION=2.108.0
ARG USER_ID=1001
ARG GROUP_ID=1001
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV CDK_USER=cdk

# TODO: fix vulnerabilities
# TODO: reduce image size

RUN apk -v --no-cache --update add \
    shadow \
    git \
    npm \
    python3 \
    py3-pip \
    aws-cli \
    make \
    jq \
    && \
    rm -rf /var/cache/apk/* && \
    npm install -g "aws-cdk@$AWS_CDK_VERSION" && \
    groupadd -g "$GROUP_ID" "$CDK_USER" && \
    useradd -l -u "$USER_ID" -g "$CDK_USER" "$CDK_USER"

VOLUME [ "/home/${CDK_USER}/.aws" ]
VOLUME [ "/app" ]

RUN mkdir -p "/home/$CDK_USER" && chown -R "$CDK_USER:$CDK_USER" "/home/$CDK_USER"
USER "$CDK_USER"
WORKDIR /app

# This is needed to build the image and distribute it. Otherwise for local testing, we mount our code directory.
#COPY --chown=cdk:cdk . /app/
COPY --chown=cdk:cdk Pipfile.lock /app/

RUN python -m pip install --upgrade pip && \
    python -m pip install pipenv
RUN python -m pipenv requirements > requirements.txt
RUN pip install -r requirements.txt

CMD ["/bin/sh"]