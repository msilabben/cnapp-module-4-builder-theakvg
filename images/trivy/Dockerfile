# Wrapper image for Trivy.
# Keep this as close to upstream as possible: do not bake vulnerability DBs into the image by default.
FROM aquasec/trivy:0.70.0@sha256:0f3a036f056e5a275aec904997a46a241955974e8a4574e24943453e80d43820 AS image

LABEL org.opencontainers.image.title="trivy-wrapper" \
      org.opencontainers.image.description="Wrapper image around upstream aquasec/trivy for GitHub CI/CD" \
      org.opencontainers.image.source="https://github.com/msilabben/cnapp-module-4-builder" \
      org.opencontainers.image.vendor="msilabben"

FROM image AS test
RUN trivy --version

FROM image AS final
