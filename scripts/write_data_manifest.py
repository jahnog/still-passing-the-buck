#!/usr/bin/env python3
"""Write a SHA256 manifest for committed replication inputs and generated paper artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_io import file_record

MANIFEST = ROOT / "data" / "file-manifest.json"

INCLUDE_PATTERNS = (
    "data/provided/*",
    "data/processed/**/*.csv",
    "data/processed/**/*.gz",
    "paper/generated/*.md",
    "paper/generated/*.json",
    "paper/generated/*.png",
)

EXCLUDE_SUFFIXES = (".meta.json",)


def iter_manifest_files() -> list[Path]:
    files: set[Path] = set()
    for pattern in INCLUDE_PATTERNS:
        for path in ROOT.glob(pattern):
            if not path.is_file():
                continue
            rel = str(path.relative_to(ROOT))
            if any(rel.endswith(suffix) for suffix in EXCLUDE_SUFFIXES):
                continue
            files.add(path)
    return sorted(files, key=lambda p: str(p.relative_to(ROOT)))


def build_manifest() -> dict[str, object]:
    return {
        "schema": 1,
        "description": "SHA256 manifest for Still Passing the Buck replication inputs and generated paper artifacts.",
        "files": [file_record(path) for path in iter_manifest_files()],
    }


def main() -> int:
    manifest = build_manifest()
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {MANIFEST.relative_to(ROOT)} ({len(manifest['files'])} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
