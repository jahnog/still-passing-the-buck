#!/usr/bin/env python3
"""Reproducible CPI–WPI inflation blend for the 1964–2006 sensitivity variant (Table 8b).

Two reproducible sources, both already in the repo's data lineage:
- CPI: the BCRA "Inflación mensual" series (API v4 series 27), continuous monthly CPI
  variation from 1943-03 — downloaded by `download_bcra_api-monetarias.py`. Each calendar
  year with all 12 months is compounded into a December-over-December log-rate.
- WPI: the INDEC wholesale-price system (SIPM) nivel-general IPIM index, base 1993 = 100 —
  the 1956–1995 serie empalmada plus the 1996+ workbook (both base-1993, so the splice is a
  plain concatenation), downloaded by the existing `download_indec_economia_sipm-*` scripts.
  December-over-December log-differences of the index.

The blend (simple average of the two log-rates) mirrors the original chapter's CPI–WPI
average convention. This feeds the notebook §9 reproducible-CPI variant only; the baseline
inflation series is not modified. The 2007–2015 official CPI values embedded in the BCRA
series carry the INDEC intervention — the variant only uses 1964–2006, and the baseline's
alternative-index override continues to govern 2007–2015.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_io import RAW_ROOT, latest_raw, processed_path, write_meta_sidecar

CPI_SOURCE = "BCRA API v4 (Estadisticas Monetarias) series 27, monthly CPI variation compounded Dec/Dec"
WPI_SOURCE = "INDEC SIPM IPIM nivel general (serie empalmada 1956-1995 + 1996+ workbook), Dec/Dec log-diff"

MONTHS = {"Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6,
          "Jul": 7, "Ago": 8, "Set": 9, "Sep": 9, "Oct": 10, "Nov": 11, "Dic": 12}


def _latest_data_file(provider: str, prefix: str) -> Path | None:
    candidate = latest_raw(provider, prefix)
    while candidate is not None and candidate.name.endswith(".meta.json"):
        data_file = candidate.parent / candidate.name[: -len(".meta.json")]
        candidate = data_file if data_file.exists() else None
    return candidate


def cpi_annual_log() -> dict[int, float]:
    raw = _latest_data_file("bcra", "api_monetarias-27-inflacion-mensual")
    if raw is None:
        raise SystemExit("Missing raw BCRA series 27; run download_bcra_api-monetarias.py first")
    monthly: dict[int, dict[int, float]] = {}
    for obs in json.loads(raw.read_text())["results"]:
        year, month = int(obs["fecha"][:4]), int(obs["fecha"][5:7])
        monthly.setdefault(year, {})[month] = float(obs["valor"])
    return {
        year: sum(math.log(1.0 + v / 100.0) for v in months.values())
        for year, months in monthly.items()
        if len(months) == 12
    }


def _december_index(xls_path: Path) -> dict[int, float]:
    """December nivel-general IPIM per year from a SIPM workbook (year header rows, month rows)."""
    frame = pd.ExcelFile(xls_path).parse(0, header=None)
    year = None
    december: dict[int, float] = {}
    for _, row in frame.iterrows():
        label = "" if pd.isna(row[0]) else str(row[0]).strip()
        if label.isdigit() and 1900 < int(label) < 2100:
            year = int(label)
        elif label[:3] in MONTHS and MONTHS[label[:3]] == 12 and year is not None:
            value = row[1]
            if isinstance(value, str):  # stray text cells with comma decimals (e.g. Dec-2001 "100,22")
                try:
                    value = float(value.strip().replace(".", "").replace(",", ".")) \
                        if "," in value else float(value.strip())
                except ValueError:
                    continue
            if isinstance(value, (int, float)) and not pd.isna(value) and value > 0:
                december[year] = float(value)
    return december


def wpi_annual_log() -> dict[int, float]:
    hist = RAW_ROOT / "indec" / "economia_sipm-serie56-95_1956-01_1995-12.xls"
    modern = RAW_ROOT / "indec" / "economia_sipm-dde1996_1996-01_2025-12.xls"
    index: dict[int, float] = {}
    if hist.exists():
        index.update({y: v for y, v in _december_index(hist).items() if y <= 1995})
    if modern.exists():
        index.update({y: v for y, v in _december_index(modern).items() if y >= 1996})
    return {
        year: math.log(index[year] / index[year - 1])
        for year in sorted(index)
        if year - 1 in index
    }


def main() -> int:
    cpi = cpi_annual_log()
    wpi = wpi_annual_log()

    rows = []
    for year in sorted(cpi):
        cpi_log = cpi[year]
        wpi_log = wpi.get(year)
        blend = (cpi_log + wpi_log) / 2.0 if wpi_log is not None else cpi_log
        rows.append(
            {
                "Year": year,
                "CPI_log": round(cpi_log, 6),
                "IPIM_log": round(wpi_log, 6) if wpi_log is not None else "",
                "Blend_log": round(blend, 6),
                "Blend_pct": round((math.exp(blend) - 1.0) * 100.0, 2),
                "Source": CPI_SOURCE + ("; " + WPI_SOURCE if wpi_log is not None else " (CPI only; no IPIM)"),
            }
        )

    df = pd.DataFrame(rows)
    out = processed_path("inflation", "cpi-wpi-blend", f"{df.Year.min()}-01", f"{df.Year.max()}-12")
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    write_meta_sidecar(
        out,
        script=Path(__file__).name,
        sources=[CPI_SOURCE, WPI_SOURCE],
        notes="Sensitivity-variant input only (notebook section 9, Table 8b); baseline inflation untouched.",
    )
    covered = [r["Year"] for r in rows if r["IPIM_log"] != ""]
    print(f"Wrote {len(df)} annual rows to {out}")
    print(f"IPIM blend coverage: {min(covered)}-{max(covered)}; CPI-only elsewhere")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
