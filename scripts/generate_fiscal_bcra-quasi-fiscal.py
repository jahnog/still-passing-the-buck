#!/usr/bin/env python3
"""Generate BCRA quasi-fiscal series from documented anchors."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import paths

ANCHORS = [
    (2001, 0.000, "measured", "No central-bank remunerated debt before Lebac (created Mar 2002)"),
    (2007, 0.055, "anchor", "End Nestor Kirchner; Lebac+Nobac ~5-6% GDP (sterilization peak)"),
    (2011, 0.040, "anchor", "End CFK I; cepo imposed Oct 2011 then sterilization eases"),
    (2015, 0.060, "anchor", "End CFK II; Lebac ARS 316550M (Dec-17-2015 Cronista) ~5.3% plus pases ~6%"),
    (2017, 0.105, "anchor", "Macri; Lebac stock over ARS 1tn (>10% GDP) — the bola de Lebac"),
    (2018, 0.095, "anchor", "Macri; Lebac peak ~11% GDP mid-2018 then unwound into Leliq by year-end"),
    (2019, 0.090, "anchor", "End Macri; Leliq+Pases ~9% GDP"),
    (2021, 0.104, "anchor", "Fernandez; Leliq+Pases 10.4% GDP (Apr 2021 Cronista)"),
    (2023, 0.100, "anchor", "End Fernandez; Leliq+Pases ~10% GDP (widely cited)"),
    (2024, 0.010, "anchor", "Milei; Pases eliminated Jul-22-2024 then migrated to Treasury (LeFi); BCRA remunerated debt ~0"),
    (2025, 0.000, "anchor", "Milei; LeFi eliminated Jul 2025; no central-bank remunerated debt"),
]
EXTRA_KNOWN = [
    (2002, 0.010, "estimate", "Lebac introduced Mar 2002; small year-end stock (~1% GDP)"),
]


def main() -> int:
    years = list(range(2001, 2026))
    data = {y: {"BCRA_QuasiFiscal_GDP": None, "Anchor": "", "Source": ""} for y in years}

    all_points = sorted(ANCHORS + EXTRA_KNOWN)
    for y, val, flag, src in all_points:
        if y in data:
            data[y]["BCRA_QuasiFiscal_GDP"] = float(val)
            data[y]["Anchor"] = flag
            data[y]["Source"] = src

    known_years = sorted([y for y, _, _, _ in all_points if y in data])
    for i in range(len(known_years) - 1):
        y0, y1 = known_years[i], known_years[i + 1]
        v0 = data[y0]["BCRA_QuasiFiscal_GDP"]
        v1 = data[y1]["BCRA_QuasiFiscal_GDP"]
        for y in range(y0 + 1, y1):
            if data[y]["BCRA_QuasiFiscal_GDP"] is None:
                frac = (y - y0) / (y1 - y0)
                data[y]["BCRA_QuasiFiscal_GDP"] = v0 + frac * (v1 - v0)
                data[y]["Anchor"] = "estimate"
                data[y]["Source"] = f"Linear interp {y0}-{y1}"

    for y in years:
        if data[y]["BCRA_QuasiFiscal_GDP"] is None:
            data[y]["BCRA_QuasiFiscal_GDP"] = 0.0
            data[y]["Anchor"] = "estimate"
            data[y]["Source"] = "extrapolated / no data"

    df = pd.DataFrame(
        {
            "Year": years,
            "BCRA_QuasiFiscal_GDP": [data[y]["BCRA_QuasiFiscal_GDP"] for y in years],
            "Anchor": [data[y]["Anchor"] for y in years],
            "Source": [data[y]["Source"] for y in years],
        }
    )

    out = paths.BCRA_QUASI_FISCAL_CSV
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} rows to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
