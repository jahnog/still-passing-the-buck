"""SHA-256 manifest for offline-regenerated notebook inputs."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import paths

MANIFEST_PATH = ROOT / "data" / "processed" / "checksums.json"


def manifest_files() -> list[Path]:
    """Processed CSVs plus the generated indicators gzip."""
    files: list[Path] = []
    processed_root = paths.PROCESSED
    if processed_root.is_dir():
        files.extend(sorted(processed_root.rglob("*.csv")))
    if paths.INDICATORS_GZ.is_file():
        files.append(paths.INDICATORS_GZ)
    return files


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest() -> dict[str, str]:
    return {str(p.relative_to(ROOT)): sha256_file(p) for p in manifest_files()}


def load_manifest() -> dict[str, str]:
    if not MANIFEST_PATH.is_file():
        raise FileNotFoundError(f"Missing checksum manifest: {MANIFEST_PATH}")
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{MANIFEST_PATH}: expected JSON object")
    return {str(k): str(v) for k, v in data.items()}


def check_manifest() -> list[str]:
    """Return human-readable mismatch messages (empty when OK)."""
    expected = load_manifest()
    problems: list[str] = []
    for rel, want in sorted(expected.items()):
        path = ROOT / rel
        if not path.is_file():
            problems.append(f"missing: {rel}")
            continue
        got = sha256_file(path)
        if got != want:
            problems.append(f"checksum mismatch: {rel} (expected {want[:12]}…, got {got[:12]}…)")
    for rel in sorted(build_manifest()):
        if rel not in expected:
            problems.append(f"untracked in manifest (run update_processed_checksums.py): {rel}")
    return problems


def write_manifest() -> dict[str, str]:
    manifest = build_manifest()
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest