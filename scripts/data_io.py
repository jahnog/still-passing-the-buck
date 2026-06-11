"""Shared helpers for download and generate scripts."""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

# --- Secret retrieval (keyring first, .env / environment fallback) ---
# This gives the desired precedence for generic secrets (S3 keys, API tokens, etc.):
# 1. keyring (encrypted via system keychain / Seahorse / Secret Service) — preferred
# 2. os.environ (populated by .env file, `uv run --env-file .env`, shell exports, CI secrets, etc.)

try:
    import keyring as _keyring
    _HAS_KEYRING = True
except ImportError:  # pragma: no cover
    _HAS_KEYRING = False

try:
    from dotenv import find_dotenv as _find_dotenv, load_dotenv as _load_dotenv
    _HAS_DOTENV = True
except ImportError:  # pragma: no cover
    _HAS_DOTENV = False

DEFAULT_SECRET_SERVICE = "stillpassingthebuck"

if _HAS_DOTENV:
    # Auto-load a .env file if present when the module is imported.
    # This makes the fallback convenient even when running scripts directly
    # (e.g. `python scripts/my_upload.py`). find_dotenv walks upward.
    # When using `uv run --env-file .env ...` the values are already in the environment,
    # so this is harmless (dotenv won't override real env vars by default).
    _load_dotenv(_find_dotenv(usecwd=True))


def get_secret(
    name: str,
    *,
    service: str = DEFAULT_SECRET_SERVICE,
    fallback_to_env: bool = True,
    set_env: bool = False,
) -> str:
    """
    Return a secret, trying the encrypted keyring first, then the process environment.

    Precedence (exactly as requested):
      1. keyring (service + name) — the secure/encrypted path using your OS keychain
         (Seahorse on GNOME, etc.). This is what the script will use on machines
         where you have stored the value with `keyring set ...`.
      2. os.environ[name] — the convenient fallback. Values here can come from:
         - A .env file (loaded automatically if python-dotenv is installed, or
           injected by `uv run --env-file .env`, direnv, shell sourcing, etc.)
         - Real environment variables
         - CI / container secrets

    Recommended naming: use the same name you would use as an environment variable
    (e.g. "AWS_ACCESS_KEY_ID"). This makes the two stores interchangeable.

    Args:
        name: Secret identifier (e.g. "AWS_ACCESS_KEY_ID", "GITHUB_TOKEN").
        service: Keyring namespace (default "stillpassingthebuck" keeps everything
                 for this project grouped together).
        fallback_to_env: Allow falling back to os.environ.
        set_env: If True and a value is found, also do os.environ[name] = value.
                 Very handy so that boto3, the AWS CLI inside the same process,
                 or other libraries that read standard env vars "just work".

    Raises:
        KeyError: if the secret is not present in either store.
    """
    if not name:
        raise ValueError("Secret name must be non-empty")

    # 1. Keyring (encrypted) — tried first
    if _HAS_KEYRING:
        try:
            value = _keyring.get_password(service, name)
            if value:
                if set_env:
                    os.environ[name] = value
                return value
        except Exception:
            # Backend unavailable (no dbus / keyring daemon, locked, headless, etc.)
            # Gracefully fall through to the environment fallback.
            pass

    # 2. Environment fallback (the ".env / .venv context" path)
    if fallback_to_env:
        value = os.environ.get(name)
        if value is not None:  # allow empty string if someone really sets it
            if set_env:
                os.environ[name] = value
            return value

    raise KeyError(
        f"Secret '{name}' not found in keyring (service={service}) "
        f"or environment.\n"
        f"  Store in keyring (recommended):  keyring set {service} {name}\n"
        f"  Or put in .env (fallback):       {name}=your-value-here\n"
        f"  Then run with:                   uv run --env-file .env python ..."
    )


def ensure_secrets_in_env(names: list[str], *, service: str = DEFAULT_SECRET_SERVICE) -> None:
    """
    Fetch the given secret names (keyring first) and ensure they are present in
    os.environ. Useful right before calling libraries that expect classic env vars
    (boto3 for AWS, etc.).
    """
    for name in names:
        # get_secret will raise if truly missing; set_env=True populates os.environ
        get_secret(name, service=service, set_env=True)


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


def write_meta_sidecar(dest: Path, *, script: str, sources: list[str], notes: str = "") -> None:
    """Write `<dest>.meta.json` recording who generated the file, from what, and when.

    The sidecar makes data revisions auditable: when an upstream source revises a series, the
    regenerated CSV gets a fresh timestamp and source list, and `data/REVISIONS.md` should be
    updated with what changed and why.
    """
    meta = {
        "file": dest.name,
        "generated_by": script,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sources": sources,
        "notes": notes,
    }
    sidecar = dest.parent / (dest.name + ".meta.json")
    sidecar.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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
