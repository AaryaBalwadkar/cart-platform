FROM python:3.12-slim

ARG TERRAFORM_VERSION=1.9.8
ARG TARGETARCH

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl unzip \
    && curl -fsSLo /tmp/terraform.zip "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_${TARGETARCH}.zip" \
    && unzip /tmp/terraform.zip -d /usr/local/bin \
    && rm -rf /tmp/terraform.zip /var/lib/apt/lists/* \
    && pip install --no-cache-dir ansible-core==2.17.7

WORKDIR /workspace
