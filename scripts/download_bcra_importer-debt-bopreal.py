#!/usr/bin/env python3
"""Download the official BCRA importer-debt workbook and audited BOPREAL note."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.bcra_importer_debt_bopreal import (
    BOPREAL_SOURCE,
    IMPORTER_DEBT_SOURCE,
    validate_bopreal_pdf,
    validate_importer_debt_xlsx,
)
from scripts.data_io import (
    atomic_write_bytes,
    fetch_bytes,
    file_sha256,
    rotation_sidecar,
    write_meta_sidecar,
)


def _download_rotating_workbook() -> None:
    source = IMPORTER_DEBT_SOURCE
    content = fetch_bytes(source.url, timeout=180)
    validate_importer_debt_xlsx(content)
    atomic_write_bytes(content, source.artifact, min_size=source.min_size)
    write_meta_sidecar(
        source.artifact,
        script=Path(__file__).name,
        sources=[source.url],
        notes=(
            f"{source.title}; living BCRA statistical workbook retained as a dated pipeline "
            "snapshot and rotated on refresh."
        ),
    )
    print(f"Wrote {source.artifact.relative_to(ROOT)}")


def _retain_or_download_pinned_pdf() -> None:
    source = BOPREAL_SOURCE
    sidecar = rotation_sidecar(source.artifact)
    if source.artifact.exists():
        content = source.artifact.read_bytes()
        validate_bopreal_pdf(content)
        if not sidecar.exists():
            raise FileNotFoundError(f"Pinned BCRA PDF lacks metadata sidecar: {sidecar}")
        metadata = json.loads(sidecar.read_text(encoding="utf-8"))
        output = metadata.get("output", {})
        if metadata.get("sources") != [source.url]:
            raise ValueError(f"Pinned BCRA PDF sidecar has the wrong source URL: {sidecar}")
        if output.get("bytes") != source.artifact.stat().st_size:
            raise ValueError(f"Pinned BCRA PDF sidecar has the wrong byte count: {sidecar}")
        if output.get("sha256") != file_sha256(source.artifact):
            raise ValueError(f"Pinned BCRA PDF sidecar has the wrong SHA-256: {sidecar}")
        print(f"Retained {source.artifact.relative_to(ROOT)}")
        return

    content = fetch_bytes(source.url, timeout=180)
    validate_bopreal_pdf(content)
    atomic_write_bytes(content, source.artifact, min_size=source.min_size)
    write_meta_sidecar(
        source.artifact,
        script=Path(__file__).name,
        sources=[source.url],
        notes=(
            f"{source.title}; final audited artifact pinned for BOPREAL Note 4.15 "
            "row-level provenance."
        ),
    )
    print(f"Wrote {source.artifact.relative_to(ROOT)}")


def main() -> int:
    _download_rotating_workbook()
    _retain_or_download_pinned_pdf()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
