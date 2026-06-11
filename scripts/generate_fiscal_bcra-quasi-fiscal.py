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

# Nominal interest accrued on the remunerated liabilities (the quasi-fiscal *flow*), % of GDP.
# ESTIMATES: stock anchors above x average policy/Lebac/Leliq rates; 2019+ magnitudes follow the
# OPC's quasi-fiscal monitoring. In triple-digit-inflation years (2023) the nominal figure is
# mostly inflation compensation, not a real burden — which is why this series only feeds the
# cash-basis consolidated debt-service *sensitivity* (notebook section 6.0 E), never the
# headline FPI.
INTEREST_ANCHORS = [
    (2001, 0.000, "measured", "No remunerated stock"),
    (2003, 0.003, "estimate", "Small Lebac stock at single-digit rates"),
    (2007, 0.007, "estimate", "Lebac+Nobac ~5-6% GDP at ~10% rates"),
    (2011, 0.005, "estimate", "Stock ~4% GDP at ~12% rates"),
    (2015, 0.015, "estimate", "Stock ~6% GDP at ~26% Lebac rates"),
    (2017, 0.028, "estimate", "Bola de Lebac: stock >10% GDP at ~26% rates"),
    (2018, 0.035, "estimate", "Rates 40-70% during the 2018 run; stock ~10% GDP"),
    (2019, 0.033, "estimate", "Leliq ~60-70% on ~9% GDP stock (OPC quasi-fiscal monitoring)"),
    (2020, 0.020, "estimate", "Rates cut to 38%; stock ~10% GDP"),
    (2021, 0.033, "estimate", "Leliq/Pases 38-48% on 10.4% GDP stock"),
    (2022, 0.045, "estimate", "Rates 44-75% through the year"),
    (2023, 0.090, "estimate", "Rates 97-133% on ~10% GDP stock; NOMINAL - mostly inflation compensation"),
    (2024, 0.015, "estimate", "Pases at 40% until the Jul-2024 migration to Treasury LeFi"),
    (2025, 0.000, "measured", "No central-bank remunerated debt after LeFi elimination"),
]

# Importer arrears / BOPREAL (the section 6.0 E paired sensitivity), USD millions outstanding at
# year-end IN EXCESS of the normal trade-credit stock. The 2022-23 arrears were invisible
# liabilities accumulated under exchange controls (BCRA import-debt survey: ~USD 58bn at
# end-2023 vs a ~USD 30bn historical norm); in 2024 they were converted into the BCRA's BOPREAL
# bonds (~USD 10bn issued), which would look like *new* debt if added one-sidedly. The paired
# add-back keeps the treatment symmetric across the 2023/2024 administration change.
TRADE_ARREARS_USD_M = [
    (2022, 8000, "estimate", "Import payment deferrals accumulate under the 2022 SIRA controls"),
    (2023, 28000, "estimate", "BCRA import-debt survey: ~USD 58bn stock vs ~USD 30bn norm"),
    (2024, 9500, "estimate", "BOPREAL series 1-3 outstanding after issuance (~USD 10bn) and early amortizations"),
    (2025, 6000, "estimate", "BOPREAL outstanding after amortizations and tax-payment redemptions"),
]


def interpolate_anchors(
    years: list[int], points: list[tuple[int, float, str, str]]
) -> dict[int, tuple[float, str, str]]:
    """Anchor values with linear interpolation between them; 0.0 outside the anchored span."""
    data: dict[int, tuple[float, str, str]] = {}
    all_points = sorted(p for p in points if p[0] in years)
    for y, val, flag, src in all_points:
        data[y] = (float(val), flag, src)

    known_years = sorted(data)
    for i in range(len(known_years) - 1):
        y0, y1 = known_years[i], known_years[i + 1]
        v0, v1 = data[y0][0], data[y1][0]
        for y in range(y0 + 1, y1):
            frac = (y - y0) / (y1 - y0)
            data[y] = (v0 + frac * (v1 - v0), "estimate", f"Linear interp {y0}-{y1}")

    for y in years:
        if y not in data:
            data[y] = (0.0, "estimate", "extrapolated / no data")
    return data


def main() -> int:
    years = list(range(2001, 2026))

    stock = interpolate_anchors(years, ANCHORS + EXTRA_KNOWN)
    interest = interpolate_anchors(years, INTEREST_ANCHORS)
    # Arrears/BOPREAL is a sparse sensitivity series: no interpolation outside its listed
    # years (it is zero before 2022 by construction, not by extrapolation).
    arrears = {y: (0.0, "", "") for y in years}
    for y, val, flag, src in TRADE_ARREARS_USD_M:
        if y in arrears:
            arrears[y] = (float(val), flag, src)

    df = pd.DataFrame(
        {
            "Year": years,
            "BCRA_QuasiFiscal_GDP": [stock[y][0] for y in years],
            "Anchor": [stock[y][1] for y in years],
            "Source": [stock[y][2] for y in years],
            "BCRA_QuasiFiscal_Interest_GDP": [interest[y][0] for y in years],
            "Interest_Anchor": [interest[y][1] for y in years],
            "Interest_Source": [interest[y][2] for y in years],
            "TradeArrears_BOPREAL_USD_M": [arrears[y][0] for y in years],
            "Arrears_Source": [arrears[y][2] for y in years],
        }
    )

    out = paths.BCRA_QUASI_FISCAL_CSV
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} rows to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
