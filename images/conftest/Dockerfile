# Wrapper image for Conftest.
# Keep this as close to upstream as possible: do not change ENTRYPOINT/CMD unless required.
FROM openpolicyagent/conftest:v0.59.0@sha256:b451f93ec386c25a4ed5aa4b835605dd4aee693374b619f5dc92374afcb6c296 AS image

LABEL org.opencontainers.image.title="conftest-wrapper" \
      org.opencontainers.image.description="Wrapper image around upstream openpolicyagent/conftest for GitHub CI/CD" \
      org.opencontainers.image.source="https://github.com/msilabben/cnapp-module-4-builder" \
      org.opencontainers.image.vendor="msilabben"

FROM image AS test
RUN conftest --version

FROM image AS final
