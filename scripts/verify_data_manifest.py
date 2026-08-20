#!/usr/bin/env python3
"""Verify the SHA256 manifest for replication inputs and generated paper artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_io import file_record

MANIFEST = ROOT / "data" / "file-manifest.json"


def main() -> int:
    if not MANIFEST.exists():
        print(f"missing manifest: {MANIFEST.relative_to(ROOT)}", file=sys.stderr)
        return 1

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    problems: list[str] = []
    for entry in manifest.get("files", []):
        rel = entry.get("path")
        path = ROOT / str(rel)
        if not path.exists():
            problems.append(f"missing file: {rel}")
            continue
        current = file_record(path)
        for field in ("bytes", "sha256"):
            if current[field] != entry.get(field):
                problems.append(
                    f"{rel}: {field} mismatch; manifest={entry.get(field)!r}, current={current[field]!r}"
                )

    if problems:
        print("Manifest verification failed:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print(f"Manifest verification passed ({len(manifest.get('files', []))} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
