"""Offline integration: regenerate processed CSVs and lock checksums."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(cmd)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


def test_make_generate_matches_checksum_manifest():
    """Regenerating from committed raw files must reproduce the locked outputs.

    `make generate` runs against the real working tree, and every generator restamps its
    `.meta.json` sidecar with the current time. The CSVs are byte-reproducible, so the
    checksum lock still holds, but the sidecars would be left dirty by a plain `make test`.
    Snapshot and restore them so running the suite never mutates tracked files.
    """
    sidecars = sorted((ROOT / "data").rglob("*.meta.json"))
    saved = {path: path.read_bytes() for path in sidecars}
    try:
        _run(["make", "generate"])
        _run([sys.executable, "scripts/check_processed_checksums.py"])
    finally:
        for path, content in saved.items():
            if path.read_bytes() != content:
                path.write_bytes(content)