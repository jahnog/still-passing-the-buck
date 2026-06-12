#!/usr/bin/env python3
"""Download the Fed H.15 annual 10-year inflation-indexed (TIPS) constant-maturity yield.

Source: DBnomics mirror of the Federal Reserve H.15 release (series
FED/H15/RIFLGFCY10_XII_N.A, annual averages, 2003 →). FRED's keyless fredgraph.csv
endpoint for DFII10 was gateway-timing-out when this script was written; the H.15 annual
series is the same instrument and is the Fed's own annual average. Feeds the curated
`data/provided/us-real-yield-10y.csv` (2003+ rows measured; pre-2003 rows remain
ESTIMATE — TIPS trade only from 1997 and H.15 coverage starts 2003)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_io import atomic_write_bytes, fetch_bytes, raw_path, write_meta_sidecar

URL = "https://api.db.nomics.world/v22/series/FED/H15/RIFLGFCY10_XII_N.A?observations=1"


def main() -> int:
    payload = fetch_bytes(URL)
    dest = raw_path("fed", "h15", "tips10y-annual", "2003-01", "2025-12", "json")
    atomic_write_bytes(payload, dest, min_size=200)
    write_meta_sidecar(
        dest,
        script=Path(__file__).name,
        sources=[URL, "Federal Reserve H.15 via DBnomics"],
        notes="Annual average 10y TIPS constant-maturity yield; updates us-real-yield-10y.csv 2003+",
    )
    print(f"Wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
