#!/usr/bin/env python3
"""Generate BCRA quasi-fiscal series: measured API year-end stocks where available,
documented anchors as fallback and cross-check.

The stock baseline uses the BCRA Estadísticas Monetarias v4 API snapshots downloaded by
`download_bcra_api-monetarias.py` (series 1258 Lebac/Nobac ARS, 1259 Lebac FX, 1260
Leliq/Notaliq, 1262 pases pasivos), valued at the last December observation of each year
against WDI nominal ARS GDP (NY.GDP.MKTP.CN). Series 1259 enters only through 2017: from
2018 the FX-letter line is LEDIV/BOPREAL, which this pipeline tracks separately in the
paired arrears/BOPREAL sensitivity (adding it here would double-count). Years without
API or GDP coverage keep the curated anchors; the anchors are always printed as a
cross-check against the measured ratios."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import paths
from scripts.data_io import latest_raw

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


# Remunerated-liability stock series in the BCRA v4 API (raw-file slug -> last year included).
# 1259 stops in 2017: see module docstring (LEDIV/BOPREAL era handled by the paired sensitivity).
STOCK_SERIES = {
    "api_monetarias-1258-lebac-nobac-ars": 2025,
    "api_monetarias-1259-lebac-nobac-fx": 2017,
    "api_monetarias-1260-leliq-notaliq": 2025,
    "api_monetarias-1262-pases-pasivos": 2025,
}
MEASURED_SOURCE = (
    "BCRA API v4 (Estadisticas Monetarias) series 1258+1260+1262 (+1259 through 2017), "
    "last December observation / WDI NY.GDP.MKTP.CN"
)
CROSS_CHECK_TOLERANCE = 0.02  # warn when |measured - anchor| exceeds 2 pp of GDP


def december_year_end(observations: list[dict]) -> dict[int, float]:
    """Last December observation per year from [{fecha: YYYY-MM-DD, valor: float}, ...]."""
    best: dict[int, tuple[str, float]] = {}
    for obs in observations:
        fecha = obs["fecha"]
        if fecha[5:7] != "12":
            continue
        year = int(fecha[:4])
        if year not in best or fecha > best[year][0]:
            best[year] = (fecha, float(obs["valor"]))
    return {year: value for year, (_, value) in best.items()}


def _latest_data_file(provider: str, prefix: str) -> Path | None:
    """Newest raw file for a prefix, skipping .meta.json sidecars."""
    candidate = latest_raw(provider, prefix)
    while candidate is not None and candidate.name.endswith(".meta.json"):
        data_file = candidate.parent / candidate.name[: -len(".meta.json")]
        candidate = data_file if data_file.exists() else None
    return candidate


def load_measured_stock_ratios() -> dict[int, float]:
    """Year-end remunerated stock / nominal GDP from raw API snapshots; {} when offline."""
    totals: dict[int, float] = {}
    for slug, last_year in STOCK_SERIES.items():
        raw = _latest_data_file("bcra", slug)
        if raw is None:
            return {}
        document = json.loads(raw.read_text())
        for year, value in december_year_end(document["results"]).items():
            if year <= last_year:
                totals[year] = totals.get(year, 0.0) + value  # millones de ARS

    gdp_raw = _latest_data_file("worldbank", "api_ny-gdp-mktp-cn")
    if gdp_raw is None:
        return {}
    gdp_rows = json.loads(gdp_raw.read_text())[1]
    gdp = {int(r["date"]): float(r["value"]) for r in gdp_rows if r["value"] is not None}

    return {
        year: (stock_m * 1e6) / gdp[year]
        for year, stock_m in sorted(totals.items())
        if year in gdp
    }


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

    measured = load_measured_stock_ratios()
    if measured:
        anchor_values = {y: v for y, v, _, _ in ANCHORS + EXTRA_KNOWN}
        print("Measured API year-end stocks vs curated anchors (% of GDP):")
        for year in sorted(measured):
            if year not in stock:
                continue
            ratio = measured[year]
            anchor = anchor_values.get(year)
            note = ""
            if anchor is not None and abs(ratio - anchor) > CROSS_CHECK_TOLERANCE:
                note = f"  WARNING: deviates from anchor {anchor:.3f} by >2 pp"
            print(f"  {year}: measured {ratio:.3f}" + (f" (anchor {anchor:.3f})" if anchor is not None else "") + note)
            stock[year] = (ratio, "measured-api", MEASURED_SOURCE)
    else:
        print("BCRA API raw snapshots not found; keeping curated anchors (offline mode)")
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
