#!/usr/bin/env python3
"""Upload everything Historical_CMPI_Extension.ipynb needs on Colab to the public S3 mirror.

The notebook auto-detects a repo checkout; outside one (e.g. Google Colab) it reads
every input from https://jnpublicdata.s3.us-east-1.amazonaws.com/still-passing-the-buck/.
This script keeps that mirror in sync: data files, .meta.json sidecars, portrait
images, and the two helper modules the notebook imports.

Credentials come from the OS keyring (service "stillpassingthebuck", see .env.example):
    keyring set stillpassingthebuck AWS_ACCESS_KEY_ID
    keyring set stillpassingthebuck AWS_SECRET_ACCESS_KEY
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_io import ensure_secrets_in_env

BUCKET = "jnpublicdata"
REGION = "us-east-1"
PREFIX = "still-passing-the-buck/"
PUBLIC_BASE = f"https://{BUCKET}.s3.{REGION}.amazonaws.com/{PREFIX}"

NOTEBOOK = ROOT / "Historical_CMPI_Extension.ipynb"
PORTRAITS_REL = "assets/portraits"

# Mirrors the notebook's path constants and inline pd.read_csv literals
# (verify_notebook_coverage() fails the run if the notebook drifts from this list).
DATA_FILES: tuple[str, ...] = (
    "data/provided/Indicators.csv.gz",
    "data/processed/interest/converted_interest_wb-ids-arg_1958-01_2025-12.csv",
    "data/provided/alt-cpi-2007-2015.csv",
    "data/processed/exchange/converted_exchange_parallel-cepo_2012-01_2025-12.csv",
    "data/processed/historical/converted_historical_historical-cmpi_1852-01_1963-12.csv",
    "data/processed/exchange/converted_exchange_paper-devaluation_1853-01_1999-12.csv",
    "data/processed/fiscal/converted_fiscal_fpi-fiscal_1853-01_2025-12.csv",
    "data/processed/historical/converted_historical_data-a-2018-excel_1853-01_1963-12.csv",
    "data/provided/data-quality-flags.csv",
    "data/processed/exchange/converted_exchange_dec-dec_1999-01_2025-12.csv",
    "data/provided/official-vs-revised-gdp-2005-2015.csv",
    "data/processed/fiscal/converted_fiscal_bcra-quasi-fiscal_2001-01_2025-12.csv",
    "data/provided/ipcba-vs-indec.csv",
    "data/provided/bcra-quasi-fiscal-historical.csv",
    "data/processed/inflation/converted_inflation_cpi-wpi-blend_1944-01_2025-12.csv",
    "data/provided/parallel-fx-historical.csv",
    "data/provided/us-real-yield-10y.csv",
)

# Helper modules the notebook bootstrap-downloads on Colab (must stay self-contained).
SCRIPT_FILES: tuple[str, ...] = (
    "scripts/cmpi_core.py",
    "scripts/presidency_portraits.py",
)

CONTENT_TYPES = {
    ".csv": "text/csv",
    ".gz": "application/gzip",  # never ContentEncoding: gzip — pandas expects raw bytes
    ".json": "application/json",
    ".jpg": "image/jpeg",
    ".py": "text/x-python",
}

LEGACY_PORTRAIT_RE = re.compile(r"^[0-9a-f]{16}\.jpg$")


def build_inventory() -> list[str]:
    """Repo-relative paths to mirror; portraits manifest excluded (Colab is manifest-free)."""
    files = list(DATA_FILES)
    files += [f"{f}.meta.json" for f in DATA_FILES if (ROOT / f"{f}.meta.json").is_file()]
    files += sorted(
        str(p.relative_to(ROOT)) for p in (ROOT / PORTRAITS_REL).glob("*.jpg")
    )
    files += list(SCRIPT_FILES)
    return files


def notebook_data_references() -> set[str]:
    """data/... string literals in the notebook's code cells."""
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    source = "".join(
        "".join(cell["source"]) for cell in nb["cells"] if cell["cell_type"] == "code"
    )
    return set(re.findall(r"[\"'](data/[^\"']+\.(?:csv|gz|xlsx))[\"']", source))


def verify_notebook_coverage(files: list[str]) -> list[str]:
    """Referenced data files that exist locally but are missing from DATA_FILES."""
    covered = set(files)
    return sorted(
        ref
        for ref in notebook_data_references()
        if ref not in covered and (ROOT / ref).is_file()
    )


def check_no_legacy_names(files: list[str]) -> list[str]:
    return [f for f in files if LEGACY_PORTRAIT_RE.match(Path(f).name)]


def md5_hex(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def remote_etag(s3, key: str) -> str | None:
    from botocore.exceptions import ClientError

    try:
        return s3.head_object(Bucket=BUCKET, Key=key)["ETag"].strip('"')
    except ClientError as exc:
        # 403 covers anonymous HEAD of a missing key on a GetObject-only public
        # bucket (no public ListBucket -> S3 hides 404 behind AccessDenied).
        if exc.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound", "403", "AccessDenied"):
            return None
        raise


def make_s3_client(*, signed: bool):
    import boto3

    if signed:
        ensure_secrets_in_env(["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"])
        return boto3.client("s3", region_name=REGION)
    from botocore import UNSIGNED
    from botocore.config import Config

    return boto3.client("s3", region_name=REGION, config=Config(signature_version=UNSIGNED))


def content_type(path: Path) -> str:
    return CONTENT_TYPES.get(path.suffix.lower(), "application/octet-stream")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print PUT/SKIP decisions without uploading anything.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Upload even when the remote ETag matches, and ignore coverage drift.",
    )
    args = parser.parse_args()

    inventory = build_inventory()

    missing_local = [f for f in inventory if not (ROOT / f).is_file()]
    if missing_local:
        for f in missing_local:
            print(f"ERROR: listed file missing locally: {f}")
        return 1

    uncovered = verify_notebook_coverage(inventory)
    if uncovered:
        for f in uncovered:
            print(f"{'WARNING' if args.force else 'ERROR'}: notebook reads {f} but it is not in DATA_FILES")
        if not args.force:
            return 1

    legacy = check_no_legacy_names(inventory)
    if legacy:
        print(f"WARNING: {len(legacy)} hash-named portraits found; run "
              "download_presidency_portraits.py --migrate-only first.")

    try:
        s3 = make_s3_client(signed=True)
    except KeyError:
        if not args.dry_run:
            raise
        # Dry runs stay useful without credentials: anonymous ETag checks against
        # the public bucket (missing/denied keys simply show as PUT).
        print("NOTE: AWS credentials unavailable; dry-run uses anonymous requests.")
        s3 = make_s3_client(signed=False)

    uploaded = skipped = 0
    failed: list[str] = []
    for rel in inventory:
        path = ROOT / rel
        key = PREFIX + rel
        try:
            if not args.force and remote_etag(s3, key) == md5_hex(path):
                skipped += 1
                print(f"SKIP {key}")
                continue
            if args.dry_run:
                uploaded += 1
                print(f"PUT  {key} (dry-run)")
                continue
            s3.put_object(
                Bucket=BUCKET,
                Key=key,
                Body=path.read_bytes(),
                ContentType=content_type(path),
            )
            uploaded += 1
            print(f"PUT  {key}")
        except Exception as exc:  # noqa: BLE001 — report every failed key at the end
            print(f"FAIL {key}: {exc}")
            failed.append(key)

    print(f"Done: uploaded={uploaded}, skipped={skipped}, failed={len(failed)}")
    print(f"Public base: {PUBLIC_BASE}")
    if failed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
