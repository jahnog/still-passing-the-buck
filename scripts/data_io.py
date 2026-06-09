"""Shared helpers for download and generate scripts."""

from __future__ import annotations

import os
import re
import sys
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = ROOT / "data" / "raw"
PROCESSED_ROOT = ROOT / "data" / "processed"
PROVIDED_ROOT = ROOT / "data" / "provided"

USER_AGENT = "StillPassingTheBuck/1.0"


def raw_path(
    provider: str,
    data_source: str,
    data_file: str,
    date_from: str,
    date_to: str,
    ext: str,
) -> Path:
    """Build `data/raw/<provider>/<data-source>_<data-file>_<from>_<to>.<ext>`."""
    name = f"{data_source}_{data_file}_{date_from}_{date_to}.{ext.lstrip('.')}"
    return RAW_ROOT / provider / name


def processed_path(
    purpose: str,
    input_token: str,
    date_from: str,
    date_to: str,
) -> Path:
    """Build `data/processed/<purpose>/converted_<purpose>_<input>_<from>_<to>.csv`."""
    name = f"converted_{purpose}_{input_token}_{date_from}_{date_to}.csv"
    return PROCESSED_ROOT / purpose / name


def rotate_existing(path: Path) -> None:
    """Rename existing file with incremental `_N` postfix before a new write."""
    if not path.exists():
        return
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    match = re.match(r"^(.+)_(\d+)$", stem)
    base = match.group(1) if match else stem
    n = 1
    while (parent / f"{base}_{n}{suffix}").exists():
        n += 1
    path.rename(parent / f"{base}_{n}{suffix}")


def atomic_write_bytes(content: bytes, dest: Path, *, min_size: int = 0) -> None:
    """Write bytes atomically: temp file, then replace; rotate existing on collision."""
    if min_size and len(content) < min_size:
        raise RuntimeError(f"Download too small ({len(content)} bytes); expected >= {min_size}")

    dest.parent.mkdir(parents=True, exist_ok=True)
    rotate_existing(dest)

    fd, tmp_name = tempfile.mkstemp(prefix=f".{dest.name}.", dir=dest.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
        os.replace(tmp_path, dest)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


def fetch_bytes(url: str, *, timeout: int = 120) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def atomic_download(url: str, dest: Path, *, timeout: int = 120, min_size: int = 0) -> None:
    """Download URL to dest using temp-then-move semantics."""
    content = fetch_bytes(url, timeout=timeout)
    atomic_write_bytes(content, dest, min_size=min_size)


def latest_raw(provider: str, prefix: str) -> Path | None:
    """Return the newest raw file under a provider matching a filename prefix."""
    folder = RAW_ROOT / provider
    if not folder.is_dir():
        return None
    matches = sorted(folder.glob(f"{prefix}*"), key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0] if matches else None


def ensure_scripts_importable() -> None:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
