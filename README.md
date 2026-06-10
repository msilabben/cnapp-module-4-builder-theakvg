# CI security tool images

This repository builds wrapper images for GitHub CI/CD pipelines.

The goal is supply-chain hardening while keeping runtime behavior as close as possible to the upstream images.

Downstream workflows should consume the published images by digest, not by tag:

```yaml
container:
  image: ghcr.io/msilabben/semgrep@sha256:REPLACE_WITH_PUBLISHED_DIGEST
  credentials:
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

## Security model

This repo intentionally keeps the model simple:

- wrapper images only
- upstream images are pinned by digest in Dockerfiles
- the upstream version is read from the same `FROM` line as the pinned digest
- images are built with `docker/build-push-action`
- workflows discover images from directories below `images/`
- pull requests build smoke-test targets and final image targets
- pushes to `main` publish images to GHCR after the `production` environment gate is approved
- images are signed with Cosign after publishing
- SBOMs are generated for published images and attached as signed Cosign attestations
- publish jobs write a GitHub job summary containing the published digest and SBOM attestation status
- no image scanning in this repository
- no policy evaluation in this repository
- no automatic downstream updates
- downstream repos pin published image digests

Tags are used for readability. Digests are used for security.

## Repository layout

```text
.
├── .github/
│   ├── dependabot.yml
│   └── workflows/
│       ├── pull-request.yml
│       └── push-main.yml
├── docs/
│   ├── downstream-example.yml
│   └── release-review.md
├── images/
│   ├── conftest/
│   │   └── Dockerfile
│   ├── semgrep/
│   │   └── Dockerfile
│   └── trivy/
│       └── Dockerfile
└── scripts/
    └── discover-images.py
```

## Initial setup checklist

Before enabling the workflows, replace all placeholders:

```bash
grep -R "REPLACE_WITH_" .
```

Required replacements:

1. Replace `msilabben` with the GitHub organization or user that owns the GHCR namespace.
2. Replace `REPLACE_WITH_REPO` with this repository name.
3. Replace every upstream image digest in each Dockerfile.
4. Replace every `REPLACE_WITH_FULL_COMMIT_SHA` in `.github/workflows` and `docs/downstream-example.yml` with a full action commit SHA. This includes the SBOM action and Cosign installer.
5. Create a GitHub Environment named `production` and configure required reviewers.
6. Configure branch protection or a repository ruleset for `main`.
7. Keep the publish workflow path filter scoped to image-builder files unless you intentionally want non-image changes to publish images.

## Tool versions

Each tool version is defined once, in the first Dockerfile stage:

```dockerfile
FROM upstream/image:version@sha256:digest AS image
```

The workflows run `scripts/discover-images.py`, which reads `version` from that line and publishes:

```text
ghcr.io/msilabben/<directory-name>:<version>
```

For example, this Dockerfile line:

```dockerfile
FROM semgrep/semgrep:1.160.0@sha256:REPLACE_WITH_UPSTREAM_DIGEST AS image
```

publishes:

```text
ghcr.io/msilabben/semgrep:1.160.0
```

A version bump should only require changing the `FROM` line in the relevant Dockerfile.

## Image discovery

The workflows call:

```bash
python3 scripts/discover-images.py
```

The script discovers every `images/*/Dockerfile`, validates that it follows this convention, and returns JSON for the GitHub Actions matrix:

```dockerfile
FROM <upstream-image>:<upstream-version>@sha256:<digest> AS image
```

The script is intentionally small and limited to discovery. It does not build, publish, scan, or enforce broad repository policy.

## Resolve upstream image digests

Example commands:

```bash
docker buildx imagetools inspect semgrep/semgrep:1.160.0
docker buildx imagetools inspect aquasec/trivy:0.70.0
docker buildx imagetools inspect openpolicyagent/conftest:v0.59.0
```

Use the digest for the platform or manifest you intentionally want to depend on. For the current baseline, this repo assumes a simple `linux/amd64` GitHub-hosted runner setup and does not attempt multi-arch publishing.

## Adding another image

Add a new directory under `images/` containing a Dockerfile with these build stages:

```dockerfile
FROM upstream/image:version@sha256:digest AS image

FROM image AS test
RUN tool --version

FROM image AS final
```

The workflows automatically include it. No workflow matrix edits are required.

## GitHub Environment gate

The publish job uses:

```yaml
environment: production
```

Configure the `production` environment in GitHub with required reviewers. This makes publishing to GHCR an explicit approval step, even after code is merged to `main`.

## Workflow permissions

Pull request workflow:

```yaml
permissions:
  contents: read
```

Publish workflow:

```yaml
permissions:
  contents: read
  packages: write
  id-token: write
```

The publish workflow needs `packages: write` to push the image and Cosign signature/attestation to GHCR. It needs `id-token: write` for keyless Cosign signing.

## SBOM attestations

The publish workflow generates an SPDX JSON SBOM for each published image and attaches it to the exact published image digest as a Cosign attestation.

The SBOM is not published as a separate package such as `semgrep-sbom`. Keeping it attached to the image digest avoids a second artifact naming scheme and makes the relationship clear:

```text
ghcr.io/msilabben/<image>@sha256:<digest>
  ├── image signature
  └── signed SBOM attestation
```

This repository still does not use the SBOM as a release gate. Reviewers and downstream consumers can decide how to use the SBOM data.

Example verification commands after replacing placeholders:

```bash
cosign verify ghcr.io/msilabben/semgrep@sha256:REPLACE_WITH_PUBLISHED_DIGEST
cosign verify-attestation --type spdxjson ghcr.io/msilabben/semgrep@sha256:REPLACE_WITH_PUBLISHED_DIGEST
```

## GitHub Actions hardening

Pin all third-party actions by full commit SHA.

Avoid:

```yaml
uses: docker/build-push-action@v6
```

Use:

```yaml
uses: docker/build-push-action@f9f3042f7e2789586610d6e8b85c8f03e5195baf
```

If available in your GitHub organization, enforce SHA-pinned actions with an organization-level Actions policy as well. Repository review is useful, but platform policy is stronger.

## Branch protection / rulesets

Recommended protection for `main`:

- require pull request before merge
- require at least one approval
- require the pull request workflow to pass
- require conversation resolution
- block force pushes
- restrict direct pushes if practical

## GHCR permissions

Recommended setup:

- Keep packages private unless there is a reason to make them public.
- Let only this image-building repository publish packages.
- Grant downstream repositories read-only package access.
- Use `GITHUB_TOKEN`, not a personal access token, unless you hit an explicit GitHub limitation.
- Keep package admin access limited to a small owner group.

Publisher workflow permissions:

```yaml
permissions:
  contents: read
  packages: write
  id-token: write
```

Downstream workflow permissions:

```yaml
permissions:
  contents: read
  packages: read
```

For private job-level containers, include credentials in the `container` block because the image is pulled before normal workflow steps run.

## Release process

1. Dependabot opens a PR when an upstream Dockerfile dependency or GitHub Action can be updated.
2. The PR workflow discovers images by reading Dockerfiles below `images/`.
3. The PR builds each image smoke-test target.
4. The PR builds each final image target without publishing.
5. A reviewer verifies the Dockerfile changes and confirms the upstream digest is intentional.
6. Merge an image-definition change to `main` to start the publish workflow.
7. The `production` environment gate requires approval before publishing.
8. The publish workflow publishes the image tag to GHCR.
9. The publish workflow generates an SPDX JSON SBOM for the published image digest.
10. The publish workflow signs the published image digest with Cosign.
11. The publish workflow attaches the SBOM as a signed Cosign attestation.
12. The publish workflow writes the published digest and SBOM attestation status to the job summary.
13. Downstream repos update to new digests manually through reviewed PRs.

## Why no `latest` tag?

`latest` adds ambiguity. It is unclear what changed, when it changed, and what reviewers approved. Use upstream-version tags for readability and digests for execution.

## Why wrapper images?

Rebuilding Semgrep, Trivy, and Conftest from source would increase maintenance burden and can make behavior drift from upstream. Wrapper images are the right starting point for your stated goal: supply-chain hardening with minimal functional changes.
