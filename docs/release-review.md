# Release review checklist

Use this checklist before approving an image update PR or approving the `production` publish environment.

## Required checks

- [ ] The upstream base image is pinned by digest in the Dockerfile `FROM` line.
- [ ] The upstream tool version and digest are both updated intentionally.
- [ ] The version only needs to be changed in the Dockerfile `FROM` line.
- [ ] GitHub Actions are pinned by full commit SHA.
- [ ] The affected wrapper image still uses the intended upstream tool.
- [ ] The smoke-test build target succeeds.
- [ ] The final image build target succeeds.
- [ ] The image behavior remains equivalent to the upstream image for expected CI usage.
- [ ] The workflow does not introduce automatic downstream updates.
- [ ] The publish job summary shows the expected GHCR image tag and digest.
- [ ] The publish job summary confirms that an SBOM was attached as a signed Cosign attestation.
- [ ] Downstream users will consume the image by digest, not by tag.

## Pushback criteria

Do not approve the PR if it:

- removes digest pinning
- switches to `latest`
- adds package installs or downloads that are not strictly needed
- combines multiple tools into one image
- bakes frequently changing policies or vulnerability databases into the tool images without a strong reason
- mutates downstream repositories automatically
- weakens GHCR permissions
- publishes SBOMs as separate packages instead of attaching them to the image digest without a clear reason
- replaces the build action with ad-hoc manual Docker commands without a clear reason
