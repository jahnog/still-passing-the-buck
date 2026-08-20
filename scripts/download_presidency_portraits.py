#!/usr/bin/env python3
"""Download and resize president/minister portraits for offline notebook display."""

from __future__ import annotations

import argparse
import sys
import time
import urllib.error
import urllib.parse
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PIL import Image

from scripts.data_io import USER_AGENT
from scripts.presidency_portraits import (
    MAX_PORTRAIT_PX,
    PORTRAIT_SOURCE_URLS,
    PORTRAITS_DIR,
    _legacy_portrait_filename,
    load_manifest,
    portrait_filename,
    portrait_relative_path,
    save_manifest,
    url_sha256_prefix,
)

WIKIMEDIA_HOST_SUFFIX = "wikimedia.org"
WIKIMEDIA_DELAY_SECONDS = 1.0
DEFAULT_HOST_DELAY_SECONDS = 0.25
MAX_RETRIES = 6
BASE_DELAY_SECONDS = 2.0
JPEG_QUALITY = 85


def host_delay_seconds(host: str) -> float:
    return WIKIMEDIA_DELAY_SECONDS if host.endswith(WIKIMEDIA_HOST_SUFFIX) else DEFAULT_HOST_DELAY_SECONDS


def wait_for_host(host: str, host_deadlines: dict[str, float], delay_seconds: float) -> None:
    """Sleep until the next allowed request time for this host, then schedule the next slot.

    If the required wait is long, print a visible message so the script does not appear to hang.
    """
    now = time.monotonic()
    deadline = host_deadlines.get(host, now)
    if deadline > now:
        wait = deadline - now
        if wait > 5:
            print(f"  Host {host} in backoff; waiting {wait:.1f}s before next request...", flush=True)
        time.sleep(wait)
    host_deadlines[host] = time.monotonic() + delay_seconds


def fetch_bytes_with_backoff(
    url: str,
    host_deadlines: dict[str, float] | None = None,
    *,
    timeout: int = 120,
) -> bytes:
    host = urllib.parse.urlparse(url).netloc
    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES):
        if attempt:
            time.sleep(host_delay_seconds(host))
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=timeout) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code == 429 and attempt + 1 < MAX_RETRIES:
                retry_after = exc.headers.get("Retry-After")
                delay = (
                    float(retry_after)
                    if retry_after and str(retry_after).isdigit()
                    else BASE_DELAY_SECONDS * (2**attempt)
                )
                print(f"  429 for {url}; sleeping {delay:.1f}s (attempt {attempt + 1}/{MAX_RETRIES})", flush=True)
                if host_deadlines is not None:
                    # Back off the whole host so the rest of the queue slows down too.
                    host_deadlines[host] = time.monotonic() + delay
                if delay > 30:
                    # Long server-mandated backoff (e.g. 10min Retry-After). Do not burn the
                    # time inside this URL's retry loop (that feels like a hang). Advance the
                    # host, print a clear message, and fail this asset for the current run.
                    # The next same-host item will announce+honor the wait via wait_for_host.
                    print(f"  Long backoff ({delay:.0f}s) requested by {host}; deferring this asset for this run.", flush=True)
                    time.sleep(min(2.0, host_delay_seconds(host)))
                    raise RuntimeError(f"Rate-limited by {host} (Retry-After {delay:.0f}s); deferred")
                time.sleep(delay)
                continue
            raise
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt + 1 < MAX_RETRIES:
                delay = BASE_DELAY_SECONDS * (2**attempt)
                print(f"  network error for {url}; sleeping {delay:.1f}s", flush=True)
                time.sleep(delay)
                continue
            raise
    assert last_error is not None
    raise last_error


def resize_to_jpeg(content: bytes) -> tuple[bytes, int, int]:
    with Image.open(BytesIO(content)) as image:
        if image.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            alpha = image.split()[-1] if image.mode in ("RGBA", "LA") else None
            background.paste(image, mask=alpha)
            image = background
        else:
            image = image.convert("RGB")
        image.thumbnail((MAX_PORTRAIT_PX, MAX_PORTRAIT_PX), Image.Resampling.LANCZOS)
        width, height = image.size
        out = BytesIO()
        image.save(out, format="JPEG", quality=JPEG_QUALITY, optimize=True)
        return out.getvalue(), width, height


def migrate_legacy_filenames() -> int:
    """Rename hash-named portraits to readable slug names. No network. Idempotent."""
    manifest = load_manifest()
    renamed = 0
    for url in PORTRAIT_SOURCE_URLS:
        legacy = PORTRAITS_DIR / _legacy_portrait_filename(url)
        dest = PORTRAITS_DIR / portrait_filename(url)
        if legacy != dest and legacy.is_file() and not dest.is_file():
            legacy.rename(dest)
            renamed += 1
        if url in manifest:
            manifest[url]["path"] = portrait_relative_path(url)
            manifest[url]["filename"] = portrait_filename(url)
    if manifest:
        save_manifest(manifest)
    return renamed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download and resize even when the local file already exists.",
    )
    parser.add_argument(
        "--migrate-only",
        action="store_true",
        help="Only rename legacy hash-named files to slug names (no network), then exit.",
    )
    args = parser.parse_args()

    PORTRAITS_DIR.mkdir(parents=True, exist_ok=True)
    renamed = migrate_legacy_filenames()
    print(f"Legacy filename migration: renamed={renamed}", flush=True)
    if args.migrate_only:
        return 0

    manifest = {} if args.force else load_manifest()

    downloaded = 0
    skipped = 0
    failed: list[str] = []
    host_deadlines: dict[str, float] = {}
    total = len(PORTRAIT_SOURCE_URLS)

    for i, url in enumerate(PORTRAIT_SOURCE_URLS, start=1):
        rel_path = portrait_relative_path(url)
        dest = ROOT / rel_path

        # Skip if we already have the file on disk (robust even if manifest is missing/stale).
        if not args.force and dest.is_file():
            skipped += 1
            if url not in manifest:
                # Opportunistically record metadata from the existing JPEG so the manifest stays complete.
                w = h = None
                try:
                    with Image.open(dest) as im:
                        w, h = im.size
                except Exception:
                    pass
                manifest[url] = {
                    "path": rel_path,
                    "filename": portrait_filename(url),
                    "sha256": url_sha256_prefix(url),
                    "width": w,
                    "height": h,
                    "source_url": url,
                }
                save_manifest(manifest)
            print(f"[{i}/{total}] Skipping (exists) {url}", flush=True)
            continue

        host = urllib.parse.urlparse(url).netloc
        wait_for_host(host, host_deadlines, host_delay_seconds(host))
        try:
            print(f"[{i}/{total}] Fetching {url}", flush=True)
            content = fetch_bytes_with_backoff(url, host_deadlines)
            jpeg, width, height = resize_to_jpeg(content)
            dest.write_bytes(jpeg)
            manifest[url] = {
                "path": rel_path,
                "filename": portrait_filename(url),
                "sha256": url_sha256_prefix(url),
                "width": width,
                "height": height,
                "source_url": url,
            }
            downloaded += 1
            save_manifest(manifest)  # incremental so interrupts don't lose work
        except Exception as exc:  # noqa: BLE001 — collect all failures, report at end
            print(f"  FAILED: {exc}", flush=True)
            failed.append(url)

    save_manifest(manifest)
    print(f"Done: downloaded={downloaded}, skipped={skipped}, failed={len(failed)}", flush=True)
    if failed:
        for url in failed:
            print(f"  - {url}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
