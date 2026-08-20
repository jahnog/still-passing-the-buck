#!/usr/bin/env python3
"""Generate BCRA quasi-fiscal series: measured API year-end stocks where available,
documented anchors as fallback and cross-check.

The stock baseline uses the BCRA Estadísticas Monetarias v4 API snapshots downloaded by
`download_bcra_api-monetarias.py` (series 1258 Lebac/Nobac ARS, 1259 Lebac FX, 1260
Leliq/Notaliq, 1262 pases pasivos), valued at the last December observation of each year
against WDI nominal ARS GDP (NY.GDP.MKTP.CN). Series 1259 enters only through 2017: from
2018 the FX-letter line is LEDIV/BOPREAL, which this pipeline tracks separately in the
paired importer-debt-increase/BOPREAL-residual correction (adding it here would
double-count). Years without
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

# Stock anchors (BCRA_QuasiFiscal_GDP — AFFECTS the FPI baseline Debt_GDP) and interest anchors
# (BCRA_QuasiFiscal_Interest_GDP — sensitivity-only, section 6.0 E) live in
# data/provided/bcra-quasi-fiscal-anchors.csv. The paired importer-debt/BOPREAL operands are
# generated from retained official BCRA artifacts in
# data/processed/fiscal/converted_fiscal_bcra-importer-debt-bopreal_2022-01_2025-12.csv.
#
# The interest series is nominal: in triple-digit-inflation years (2023) it is mostly inflation
# compensation, not a real burden — which is why it only feeds the section 6.0 E sensitivity.
# The 2022-23 arrears were invisible liabilities accumulated under exchange controls (BCRA
# import-debt survey ~USD 58bn at end-2023 vs a ~USD 30bn norm), converted into BOPREAL bonds in
# 2024; the paired add-back keeps the 2023/2024 administration change symmetric.


def load_anchor_points(variable: str) -> list[tuple[int, float, str, str]]:
    """Load (year, value, type, source-note) points from the curated quasi-fiscal anchors."""
    df = pd.read_csv(paths.BCRA_QF_ANCHORS_CSV)
    df = df[df["Variable"] == variable]
    if df.empty:
        raise RuntimeError(f"No anchor rows found for variable {variable!r}")
    points: list[tuple[int, float, str, str]] = []
    for _, row in df.iterrows():
        for field in ("Source", "Note"):
            val = row.get(field)
            if pd.isna(val) or not str(val).strip():
                raise ValueError(
                    f"BCRA anchors CSV: {variable} year {row['Year']} missing required {field!r}"
                )
        points.append((int(row["Year"]), float(row["Value"]), str(row["Type"]), str(row["Note"])))
    return points


def load_importer_debt_bopreal() -> list[tuple[int, float, str, str]]:
    """Load the four official operands generated from the BCRA XLSX and audited PDF."""
    path = paths.BCRA_IMPORTER_DEBT_BOPREAL_CSV
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}; run generate_fiscal_bcra-importer-debt-bopreal.py first"
        )
    frame = pd.read_csv(path)
    required = {"Year", "Measure", "Value_USD_M", "SourceID", "SourceLocator"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"{path.name}: missing required columns {sorted(missing)}")
    if frame["Year"].astype(int).tolist() != [2022, 2023, 2024, 2025]:
        raise ValueError(f"{path.name}: expected exactly years 2022–2025")
    expected_measures = {
        2022: "ImporterDebtIncrease",
        2023: "ImporterDebtIncrease",
        2024: "BOPREALResidual",
        2025: "BOPREALResidual",
    }
    points: list[tuple[int, float, str, str]] = []
    for _, row in frame.iterrows():
        year = int(row["Year"])
        measure = str(row["Measure"])
        if measure != expected_measures[year]:
            raise ValueError(
                f"{path.name}: year {year} has measure {measure!r}, "
                f"expected {expected_measures[year]!r}"
            )
        source = f"{measure}; {row['SourceID']}; {row['SourceLocator']}"
        points.append((year, float(row["Value_USD_M"]), "measured-official", source))
    return points


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

    stock_points = load_anchor_points("BCRA_QuasiFiscal_GDP")
    stock = interpolate_anchors(years, stock_points)

    measured = load_measured_stock_ratios()
    if measured:
        anchor_values = {y: v for y, v, _, _ in stock_points}
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
    interest = interpolate_anchors(years, load_anchor_points("BCRA_QuasiFiscal_Interest_GDP"))
    # The importer-debt/BOPREAL operand is sparse: no interpolation outside its listed years
    # (it is zero before 2022 by construction, not by extrapolation).
    arrears = {y: (0.0, "", "") for y in years}
    for y, val, flag, src in load_importer_debt_bopreal():
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
            "Arrears_Flag": [arrears[y][1] for y in years],
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
