#!/usr/bin/env python3
"""Generate Argentina WDI indicators from the bulk WDI zip plus official overlays."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.paths import INDICATORS_CSV, INDICATORS_GZ
from scripts.data_io import latest_raw
from scripts.indicator_build import build_indicator_rows, write_indicators

REQUIRED_CODES = (
    "NY.GDP.PCAP.KD.ZG",
    "NY.GDP.MKTP.CD",
    "BX.GSR.TOTL.CD",
    "NY.GDP.MKTP.KD",
    "NE.EXP.GNFS.CD",
    "NE.EXP.GNFS.KD",
    "NY.GDP.DEFL.KD.ZG",
    "PA.NUS.ATLS",
    "FP.WPI.TOTL",
    "NY.GDP.MKTP.KD.ZG",
)


def _wdi_zip() -> Path:
    path = latest_raw("worldbank", "wdi_wdi-csv")
    if path is None or path.suffix.lower() != ".zip":
        raise RuntimeError(
            "Missing World Bank WDI bulk zip; run download_worldbank_wdi_wdi-csv.py."
        )
    return path


def main() -> int:
    try:
        zip_path = _wdi_zip()
        rows = build_indicator_rows(zip_path=zip_path)
        missing: list[str] = []
        for code in REQUIRED_CODES:
            if code == "NY.GDP.MKTP.KD.ZG":
                if (code, 2025) not in rows and (code, 2024) not in rows:
                    missing.append(f"{code} 2024")
            elif (code, 2025) not in rows:
                missing.append(f"{code} 2025")
        if missing:
            raise RuntimeError(
                "Indicator overlay is missing required observations: "
                + ", ".join(missing)
                + ". Run download_worldbank_api_indicators-arg.py."
            )
        write_indicators(rows, INDICATORS_CSV, INDICATORS_GZ)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Wrote {len(rows)} Argentina indicator rows to {INDICATORS_CSV}")
    print(f"Compressed {INDICATORS_GZ}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
