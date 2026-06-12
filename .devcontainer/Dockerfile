FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

ARG COSIGN_VERSION=v3.0.2
ARG GRYPE_VERSION=v0.104.0

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl tar \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL \
      "https://github.com/sigstore/cosign/releases/download/${COSIGN_VERSION}/cosign-linux-amd64" \
      -o /usr/local/bin/cosign \
    && chmod +x /usr/local/bin/cosign \
    && cosign version

RUN curl -fsSL \
      "https://github.com/anchore/grype/releases/download/${GRYPE_VERSION}/grype_${GRYPE_VERSION#v}_linux_amd64.tar.gz" \
      -o /tmp/grype.tar.gz \
    && tar -xzf /tmp/grype.tar.gz -C /tmp grype \
    && mv /tmp/grype /usr/local/bin/grype \
    && chmod +x /usr/local/bin/grype \
    && rm /tmp/grype.tar.gz \
    && grype version