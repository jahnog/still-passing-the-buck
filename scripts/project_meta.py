"""Project metadata from pyproject.toml."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def project_version(root: Path | None = None) -> str:
    """Return ``[project].version`` from pyproject.toml."""
    path = (root or ROOT) / "pyproject.toml"
    with path.open("rb") as handle:
        return tomllib.load(handle)["project"]["version"]
