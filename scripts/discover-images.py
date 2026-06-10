#!/usr/bin/env python3
"""Discover image build definitions below images/.

The GitHub workflows use this script to build their matrix. Each image is a
subdirectory below images/ containing a Dockerfile whose first wrapper stage uses
this convention:

    FROM <upstream-image>:<upstream-version>@sha256:<digest> AS image

The upstream version becomes the GHCR tag for the wrapper image.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path("images")
FROM_RE = re.compile(
    r"^FROM\s+"
    r"(?P<upstream>[^\s:@]+(?:/[^\s:@]+)*):"
    r"(?P<version>[^@\s]+)"
    r"@sha256:(?P<digest>[^\s]+)"
    r"\s+AS\s+image\s*$",
    re.IGNORECASE,
)


def fail(message: str) -> None:
    print(f"::error::{message}", file=sys.stderr)
    raise SystemExit(1)


def read_image(dockerfile: Path) -> dict[str, str]:
    context = dockerfile.parent
    name = context.name

    from_line = ""
    for line in dockerfile.read_text(encoding="utf-8").splitlines():
        if line.upper().startswith("FROM ") and " AS image" in line:
            from_line = line.strip()
            break

    if not from_line:
        fail(
            f"{dockerfile}: expected wrapper stage: "
            "FROM <image>:<version>@sha256:<digest> AS image"
        )

    match = FROM_RE.match(from_line)
    if not match:
        fail(
            f"{dockerfile}: could not parse version from: {from_line}. "
            "Use: FROM <image>:<version>@sha256:<digest> AS image"
        )

    return {
        "name": name,
        "context": str(context),
        "version": match.group("version"),
        "upstream": match.group("upstream"),
        "from": from_line,
    }


def main() -> None:
    dockerfiles = sorted(ROOT.glob("*/Dockerfile"))
    if not dockerfiles:
        fail("No Dockerfiles found below images/.")

    images = [read_image(dockerfile) for dockerfile in dockerfiles]
    print(json.dumps(images, separators=(",", ":")))


if __name__ == "__main__":
    main()
