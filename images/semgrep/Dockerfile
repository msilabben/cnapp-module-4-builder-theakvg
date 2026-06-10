# Wrapper image for Semgrep.
# Keep this as close to upstream as possible: do not change ENTRYPOINT/CMD unless required.
FROM semgrep/semgrep:1.160.0@sha256:f4791a54c891eabe1188248135574e6e03dfc31dfd3f3b747c7bec7079bfed1b AS image

LABEL org.opencontainers.image.title="semgrep-wrapper" \
      org.opencontainers.image.description="Wrapper image around upstream semgrep/semgrep for GitHub CI/CD" \
      org.opencontainers.image.source="https://github.com/msilabben/cnapp-module-4-builder" \
      org.opencontainers.image.vendor="msilabben"

FROM image AS test
RUN semgrep --version

FROM image AS final
