#!/usr/bin/env python3
"""Generate data/argentina/fiscal/bcra-quasi-fiscal-2001-2025.csv from documented anchors.

This makes the BCRA quasi-fiscal (remunerated liabilities) series fully reproducible,
matching the methodology and sources described in data/argentina/README.md.

Anchors are taken from known public figures and contemporary reporting (Cronista,
BCRA-related disclosures, etc.). Values between anchors are linearly interpolated
as "estimate". The 2001 starting point is "measured" (zero before Lebac creation).

Run:
  ./.venv/bin/python scripts/_gen_bcra_quasi_fiscal.py

The output is committed so the notebook and build scripts have no network dependency,
but regenerating from this script ensures the numbers + provenance stay in sync.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

OUTPUT = Path("data/argentina/fiscal/bcra-quasi-fiscal-2001-2025.csv")

# Explicit documented anchors (year, value as fraction of GDP, flag, source note).
# These are the "known good" points. Everything else is interpolated or carried.
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

# Known point for 2002 (small initial stock) — treat as anchor for interpolation start.
# The CSV treats 2002 as estimate, but we include a soft anchor for the ramp.
EXTRA_KNOWN = [
    (2002, 0.010, "estimate", "Lebac introduced Mar 2002; small year-end stock (~1% GDP)"),
]


def main() -> None:
    # Build a clean year index 2001-2025
    years = list(range(2001, 2026))

    # Start with NaN, then place all known points
    data = {y: {"BCRA_QuasiFiscal_GDP": None, "Anchor": "", "Source": ""} for y in years}

    all_points = sorted(ANCHORS + EXTRA_KNOWN)
    for y, val, flag, src in all_points:
        if y in data:
            data[y]["BCRA_QuasiFiscal_GDP"] = float(val)
            data[y]["Anchor"] = flag
            data[y]["Source"] = src

    # Linear interpolation for missing (estimate) years between anchors
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

    # Fill any remaining pre-first or post-last as 0 / measured if needed (defensive)
    for y in years:
        if data[y]["BCRA_QuasiFiscal_GDP"] is None:
            data[y]["BCRA_QuasiFiscal_GDP"] = 0.0
            data[y]["Anchor"] = "estimate"
            data[y]["Source"] = "extrapolated / no data"

    # Build DataFrame in the exact schema used by the rest of the pipeline
    df = pd.DataFrame(
        {
            "Year": years,
            "BCRA_QuasiFiscal_GDP": [data[y]["BCRA_QuasiFiscal_GDP"] for y in years],
            "Anchor": [data[y]["Anchor"] for y in years],
            "Source": [data[y]["Source"] for y in years],
        }
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False)

    print(f"Wrote {len(df)} rows to {OUTPUT}")
    print("Sample anchors preserved:")
    for y in [2001, 2007, 2015, 2017, 2023, 2024, 2025]:
        row = df[df.Year == y].iloc[0]
        print(f"  {y}: {row.BCRA_QuasiFiscal_GDP:.3f}  [{row.Anchor}]  {row.Source[:60]}...")

    # Quick round-trip sanity: the values at anchor years must match exactly
    for y, expected, flag, _ in ANCHORS:
        actual = float(df[df.Year == y]["BCRA_QuasiFiscal_GDP"].iloc[0])
        assert abs(actual - expected) < 1e-9, f"Anchor mismatch at {y}: {actual} != {expected}"
    print("\nAnchor round-trip check: OK")


if __name__ == "__main__":
    main()
