FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

ARG COSIGN_VERSION=v3.0.2

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL \
      "https://github.com/sigstore/cosign/releases/download/${COSIGN_VERSION}/cosign-linux-amd64" \
      -o /usr/local/bin/cosign \
    && chmod +x /usr/local/bin/cosign \
    && cosign version