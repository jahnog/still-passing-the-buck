"""Shared helpers for download and generate scripts."""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import hashlib
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


def file_sha256(path: Path) -> str:
    """Return the SHA256 digest for a local file."""
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_record(path: Path, *, root: Path = ROOT) -> dict[str, object]:
    """Return reproducibility metadata for a local file."""
    try:
        name = str(path.relative_to(root))
    except ValueError:
        name = str(path)
    return {
        "path": name,
        "bytes": path.stat().st_size,
        "sha256": file_sha256(path),
    }


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


# Rotation backups are `canonical_stem_N.ext` with N in 1..99. Dest names often
# end in `_YYYY-MM` or `_YYYY`; those year/month tokens are not generations.
_ROTATION_GEN = r"(?P<gen>[1-9]\d{0,1})"
_ROTATION_SUFFIX = r"(?P<suffix>\.[^.]+)"
DATED_DEST_RE = re.compile(rf"^.+_\d{{4}}-\d{{2}}{_ROTATION_SUFFIX}$")
DATED_BACKUP_RE = re.compile(rf"^(?P<stem>.+_\d{{4}}-\d{{2}})_{_ROTATION_GEN}{_ROTATION_SUFFIX}$")
UNDATED_BACKUP_RE = re.compile(rf"^(?P<stem>.+)_{_ROTATION_GEN}{_ROTATION_SUFFIX}$")
DEFAULT_ROTATION_KEEP = 2


def parse_rotated_filename(name: str) -> tuple[str, int]:
    """Return `(canonical_name, generation)` for a raw download filename.

    The live dest is generation 0. Older copies written by `rotate_existing`
    are `canonical_stem_N.ext` with N starting at 1. Dated dests such as
    `deuda_deuda-publica_2019-01_2019-12.xlsx` stay canonical; only an extra
    `_N` after that stamp is a backup. Four-digit years (`imig-anual_2017.xlsx`)
    are also left intact.
    """
    match = DATED_BACKUP_RE.match(name)
    if match:
        return f"{match.group('stem')}{match.group('suffix')}", int(match.group("gen"))
    if DATED_DEST_RE.match(name):
        return name, 0
    match = UNDATED_BACKUP_RE.match(name)
    if match:
        return f"{match.group('stem')}{match.group('suffix')}", int(match.group("gen"))
    return name, 0


def rotation_sidecar(path: Path) -> Path:
    """Return the `.meta.json` sidecar path for a raw artifact."""
    return path.with_name(path.name + ".meta.json")


def rotated_backup_path(path: Path, generation: int = 1) -> Path:
    """Return the `_N` backup path for a live dest."""
    if generation < 1:
        raise ValueError("generation must be >= 1")
    return path.with_name(f"{path.stem}_{generation}{path.suffix}")


def rotate_existing(path: Path) -> None:
    """Rename the live dest to the next free `_N` backup before a new write.

    Generation numbers increment (`_1`, then `_2`, …) and never reuse a gap, so
    the highest `_N` is always the previous dest. Year tokens in dest names are
    not generations: `imig-anual_2017.xlsx` rotates to `imig-anual_2017_1.xlsx`.
    A dest `.meta.json` sidecar, when present, moves with the file.
    """
    if not path.exists():
        return
    _, generation = parse_rotated_filename(path.name)
    if generation != 0:
        raise ValueError(f"Refusing to rotate a backup path: {path.name}")

    family = iter_rotation_family(path)
    next_gen = max((gen for gen, _member in family), default=0) + 1
    backup = rotated_backup_path(path, next_gen)
    sidecar = rotation_sidecar(path)
    path.rename(backup)
    if sidecar.exists():
        sidecar.rename(rotation_sidecar(backup))


def iter_rotation_family(path: Path) -> list[tuple[int, Path]]:
    """Return `(generation, path)` members that share `path`'s dest name.

    Newest first: the live dest, then descending `_N`.
    """
    canonical, _ = parse_rotated_filename(path.name)
    parent = path.parent
    if not parent.is_dir():
        return []
    members: list[tuple[int, Path]] = []
    for candidate in parent.iterdir():
        if not candidate.is_file() or candidate.name.startswith("."):
            continue
        if candidate.name.endswith(".meta.json"):
            continue
        name, generation = parse_rotated_filename(candidate.name)
        if name == canonical:
            members.append((generation, candidate))
    members.sort(key=lambda item: (item[0] == 0, item[0]), reverse=True)
    return members


def prune_rotated_versions(
    path: Path,
    *,
    keep: int = DEFAULT_ROTATION_KEEP,
    dry_run: bool = False,
) -> list[Path]:
    """Keep the newest `keep` copies of a rotated dest; delete older ones.

    Newest is the live dest (no `_N`), then descending generation number. Each
    deleted artifact also drops its `.meta.json` sidecar when present.
    """
    if keep < 1:
        raise ValueError("keep must be >= 1")
    removed: list[Path] = []
    for _generation, member in iter_rotation_family(path)[keep:]:
        sidecar = rotation_sidecar(member)
        sidecar_exists = sidecar.exists()
        if not dry_run:
            member.unlink()
            sidecar.unlink(missing_ok=True)
        removed.append(member)
        if sidecar_exists:
            removed.append(sidecar)
    return removed


def cleanup_rotated_raw(
    root: Path = RAW_ROOT,
    *,
    keep: int = DEFAULT_ROTATION_KEEP,
    dry_run: bool = False,
) -> list[Path]:
    """Prune every rotated download family under `root` down to `keep` copies."""
    if not root.is_dir():
        return []
    seen: set[tuple[Path, str]] = set()
    removed: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        if path.name.endswith(".meta.json") or path.name == ".gitkeep":
            continue
        canonical, _ = parse_rotated_filename(path.name)
        key = (path.parent.resolve(), canonical)
        if key in seen:
            continue
        seen.add(key)
        removed.extend(prune_rotated_versions(path, keep=keep, dry_run=dry_run))
    return removed


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
    prune_rotated_versions(dest)


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

    The sidecar makes data vintages auditable: when an upstream source revises a series, the
    regenerated CSV gets a fresh timestamp and source list.
    """
    meta = {
        "file": dest.name,
        "generated_by": script,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "output": file_record(dest),
        "sources": sources,
        "notes": notes,
    }
    sidecar = dest.parent / (dest.name + ".meta.json")
    sidecar.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_curated_sidecar(
    dest: Path,
    *,
    version: str,
    sources: list[str],
    notes: str = "",
    extra: dict | None = None,
) -> None:
    """Write `<dest>.meta.json` for a hand-curated provided CSV (version-stamped, not generated)."""
    meta = {
        "file": dest.name,
        "curated": True,
        "version": version,
        "curated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sources": sources,
        "notes": notes,
    }
    if extra:
        meta.update(extra)
    sidecar = dest.parent / (dest.name + ".meta.json")
    sidecar.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def latest_raw(provider: str, prefix: str) -> Path | None:
    """Return the newest raw file under a provider matching a filename prefix.

    Sidecars (``*.meta.json``) are ignored. When a live dest and rotated
    ``_N`` backups both match, the live dest wins.
    """
    folder = RAW_ROOT / provider
    if not folder.is_dir():
        return None
    matches = [
        path
        for path in folder.glob(f"{prefix}*")
        if path.is_file() and not path.name.endswith(".meta.json")
    ]
    if not matches:
        return None
    live = [path for path in matches if parse_rotated_filename(path.name)[1] == 0]
    pool = live or matches
    return max(pool, key=lambda path: path.stat().st_mtime)


def ensure_scripts_importable() -> None:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
