#!/usr/bin/env python3
"""December-quotation ARS/US$ devaluation series for 2000-2025.

The paper measures devaluation as the log-difference of *December quotations* (Ruíz 1990 /
DATAFIEL through 1999). The modern extension previously used WDI annual averages from 2000,
which blend pre- and post-devaluation months exactly as documented for 1963/1975/1991. This
generator restores the paper's December convention for 2000-2025:

- 1999-2001: exactly 1 ARS/USD (Ley de Convertibilidad 23,928, in force until Jan-2002).
- 2002-2025 non-cepo years: December monthly-average TCNPM from the BCRA com3500 workbook.
- Cepo years (2012-2015, 2019-2025): December daily-average of the free-market rate
  (CCL from argentinadatos; blue for 2012, before CCL quotes begin), matching the cepo
  override of the annual-average series.

Output: Year, DecRate, RateSource, DevaluationLog (log-diff vs previous December; 2000+).
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np

from data import paths
from scripts.data_io import latest_raw, write_meta_sidecar

FIRST_YEAR = 1999  # base December for the 2000 log-diff
LAST_YEAR = 2025
CEPO_YEARS = {2012, 2013, 2014, 2015, 2019, 2020, 2021, 2022, 2023, 2024, 2025}
BLUE_YEARS = {2012}  # CCL not quoted before 2013
CONVERTIBILITY = {1999: 1.0, 2000: 1.0, 2001: 1.0}
MIN_DECEMBER_OBSERVATIONS = 10


def december_tcnpm() -> dict[int, float]:
    raw = latest_raw("bcra", "publicaciones_com3500")
    if raw is None:
        raise RuntimeError("No raw BCRA com3500 workbook; run download_bcra_publicaciones_com3500.py")
    sheet = pd.read_excel(raw, sheet_name="Serie de TCNPM", header=None)
    out: dict[int, float] = {}
    for _, row in sheet.iterrows():
        stamp, value = row.iloc[1], row.iloc[2]
        if not hasattr(stamp, "month") or stamp.month != 12:
            continue
        try:
            out[int(stamp.year)] = float(value)
        except (TypeError, ValueError):
            continue
    return out


def december_free_market(year: int) -> float:
    source = "blue" if year in BLUE_YEARS else "ccl"
    raw = latest_raw("argentinadatos", f"api_cotizaciones-{source}")
    if raw is None:
        raise RuntimeError(f"No raw argentinadatos {source} file for {year}")
    quotes = json.loads(raw.read_text(encoding="utf-8"))
    december = [
        float(q["venta"])
        for q in quotes
        if str(q.get("fecha", "")).startswith(f"{year}-12") and q.get("venta")
    ]
    if len(december) < MIN_DECEMBER_OBSERVATIONS:
        raise RuntimeError(f"Only {len(december)} December-{year} {source} quotes; expected >= {MIN_DECEMBER_OBSERVATIONS}")
    return statistics.mean(december)


def main() -> int:
    official = december_tcnpm()

    rows = []
    rates: dict[int, float] = {}
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        if year in CONVERTIBILITY:
            rate, source = CONVERTIBILITY[year], "convertibility-peg"
        elif year in CEPO_YEARS:
            rate = december_free_market(year)
            source = "blue-december-avg" if year in BLUE_YEARS else "ccl-december-avg"
        else:
            if year not in official:
                raise RuntimeError(f"No December TCNPM for {year} in com3500")
            rate, source = official[year], "bcra-tcnpm-december"
        rates[year] = rate
        dlog = np.log(rates[year] / rates[year - 1]) if year - 1 in rates else None
        rows.append({"Year": year, "DecRate": round(rate, 4), "RateSource": source,
                     "DevaluationLog": round(dlog, 6) if dlog is not None else ""})

    df = pd.DataFrame(rows)
    assert len(df) == LAST_YEAR - FIRST_YEAR + 1
    assert (df["DecRate"] > 0).all()

    out = paths.DEC_DEC_MODERN_CSV
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    write_meta_sidecar(
        out,
        script=Path(__file__).name,
        sources=[
            "data/raw/bcra/publicaciones_com3500_*.xls (TCNPM December monthly average)",
            "data/raw/argentinadatos/api_cotizaciones-ccl_*.json (December daily average, cepo years)",
            "data/raw/argentinadatos/api_cotizaciones-blue_*.json (December 2012)",
            "Ley de Convertibilidad 23,928 (1999-2001 = 1 ARS/USD)",
        ],
        notes="December-quotation devaluation for 2000-2025, extending the paper's convention "
              "(Ruiz 1990 / DATAFIEL December quotations) past 1999.",
    )
    print(f"Wrote {len(df)} rows to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
