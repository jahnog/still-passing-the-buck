#!/usr/bin/env python3
"""Generate headline fiscal corrections from retained official peso operands."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import paths
from scripts.data_io import write_meta_sidecar
from scripts.hacienda_spn_base_caja import load_spn_base_caja_actuals
from scripts.official_correction_sources import SOURCES
from scripts.wb_raw import wb_series_from_raw

REQUIRED_COLUMNS = {
    "ProvenanceID",
    "Year",
    "Month",
    "CorrectionClass",
    "Item",
    "Amount_ARS_M",
    "SourceID",
    "SourceLocator",
    "ExtractionMethod",
    "Uncertainty",
}
BLOCKED_MODEL_TERMS = (
    "law 26.476",
    "dolar-soja",
    "dólar-soja",
    "unpaid interest",
    "paris club",
)


def _validate_operands(frame: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"official fiscal operands missing columns: {sorted(missing)}")
    for column in REQUIRED_COLUMNS - {"Month"}:
        if frame[column].isna().any() or not frame[column].astype(str).str.strip().all():
            raise ValueError(f"official fiscal operands contain blank {column}")
    if frame["ProvenanceID"].duplicated().any():
        raise ValueError("official fiscal operand ProvenanceID values must be unique")
    known_sources = {source.source_id for source in SOURCES}
    unknown = sorted(set(frame["SourceID"]) - known_sources)
    if unknown:
        raise ValueError(f"official fiscal operands use unknown source IDs: {unknown}")
    searchable = (frame["ProvenanceID"].astype(str) + " " + frame["Item"].astype(str)).str.lower()
    for term in BLOCKED_MODEL_TERMS:
        if searchable.str.contains(term, regex=False).any():
            raise ValueError(f"removed F-05 model reappeared in official operands: {term}")
    one_offs = frame[frame["CorrectionClass"] == "one-off"]
    if set(one_offs["Year"].astype(int)) & {2022, 2023}:
        raise ValueError("dólar-soja counterfactuals must not re-enter the official baseline")


def main() -> int:
    operands = pd.read_csv(paths.OFFICIAL_FISCAL_OPERANDS_CSV)
    _validate_operands(operands)

    years = sorted(set(operands["Year"].astype(int)))
    actuals = load_spn_base_caja_actuals(years, round_digits=None)
    gdp_lcu = wb_series_from_raw("NY.GDP.MKTP.CN")

    one_offs = operands[operands["CorrectionClass"] == "one-off"].copy()
    one_offs["CurrentRevenue_ARS_M"] = one_offs["Year"].map(
        lambda year: actuals[int(year)].current_revenue
    )
    one_offs["NominalGDP_ARS_M"] = one_offs["Year"].map(
        lambda year: float(gdp_lcu[int(year)]) / 1_000_000
    )
    one_offs["Amount_pct_revenues"] = (
        one_offs["Amount_ARS_M"] / one_offs["CurrentRevenue_ARS_M"] * 100
    )
    one_offs["Amount_pct_GDP"] = one_offs["Amount_ARS_M"] / one_offs["NominalGDP_ARS_M"] * 100
    one_offs["Type"] = "one-off"
    one_offs["Source"] = one_offs["SourceID"]
    one_offs = one_offs[
        [
            "ProvenanceID",
            "Year",
            "Item",
            "Amount_ARS_M",
            "CurrentRevenue_ARS_M",
            "NominalGDP_ARS_M",
            "Amount_pct_GDP",
            "Amount_pct_revenues",
            "Type",
            "SourceID",
            "SourceLocator",
            "ExtractionMethod",
            "Uncertainty",
            "Source",
        ]
    ].sort_values(["Year", "ProvenanceID"])
    paths.OFFICIAL_ONE_OFFS_CSV.parent.mkdir(parents=True, exist_ok=True)
    one_offs.to_csv(paths.OFFICIAL_ONE_OFFS_CSV, index=False, float_format="%.9f")
    write_meta_sidecar(
        paths.OFFICIAL_ONE_OFFS_CSV,
        script=Path(__file__).name,
        sources=[
            str(paths.OFFICIAL_FISCAL_OPERANDS_CSV.relative_to(ROOT)),
            "data/raw/bcra/publicaciones_informe-congreso_*.pdf",
            "data/raw/afip/*.pdf",
            "data/raw/opc/presupuesto_descripcion-general-2022_2021-09_2021-09.pdf",
            "data/raw/hacienda/spn-base-caja_valores-anuales_*.csv",
            "data/raw/worldbank/api_ny-gdp-mktp-cn_*.json",
        ],
        notes=(
            "Every percentage is generated from a retained official peso operand. "
            "Amount_pct_revenues uses dataset-379 SPN current revenue; Amount_pct_GDP uses "
            "the committed World Bank nominal-GDP snapshot. No counterfactual amount is included."
        ),
    )

    cap = operands[operands["CorrectionClass"] == "capitalized-interest"].copy()
    cap["Year"] = cap["Year"].astype(int)
    cap_rows: list[dict[str, object]] = []
    for year, group in cap.groupby("Year"):
        capitalized = float(group["Amount_ARS_M"].sum())
        cash_interest = float(actuals[int(year)].interest_measure)
        nominal_gdp = float(gdp_lcu[int(year)]) / 1_000_000
        cap_rows.append(
            {
                "ProvenanceID": f"fiscal-capitalized-interest-{year}-annual",
                "Year": int(year),
                "CashInterest_ARS_M": cash_interest,
                "CapitalizedInterest_ARS_M": capitalized,
                "NominalGDP_ARS_M": nominal_gdp,
                "CashInterest_GDP": cash_interest / nominal_gdp,
                "CapitalizedInterest_GDP": capitalized / nominal_gdp,
                "SourceIDs": ";".join(group.sort_values("Month")["SourceID"].astype(str)),
                "SourceLocators": "; ".join(
                    group.sort_values("Month")["SourceLocator"].astype(str)
                ),
                "ExtractionFormula": (
                    "sum official monthly/system-record capitalized-interest peso operands; "
                    "divide cash and capitalized amounts by WDI NY.GDP.MKTP.CN / 1e6"
                ),
                "Uncertainty": "; ".join(sorted(set(group["Uncertainty"].astype(str)))),
            }
        )
    capitalized = pd.DataFrame(cap_rows).sort_values("Year")
    capitalized.to_csv(
        paths.OFFICIAL_CAPITALIZED_INTEREST_CSV,
        index=False,
        float_format="%.9f",
    )
    write_meta_sidecar(
        paths.OFFICIAL_CAPITALIZED_INTEREST_CSV,
        script=Path(__file__).name,
        sources=[
            str(paths.OFFICIAL_FISCAL_OPERANDS_CSV.relative_to(ROOT)),
            "data/raw/opc/deuda_operaciones-publicas_2024-12_2024-12.pdf",
            "data/raw/opc/deuda_operaciones-publicas_2025-*_2025-*.pdf",
            "data/raw/hacienda/spn-base-caja_valores-anuales_*.csv",
            "data/raw/worldbank/api_ny-gdp-mktp-cn_*.json",
        ],
        notes=(
            "Cash interest comes from dataset 379; capitalized interest comes from OPC's "
            "official debt-operation records. The 2025 sum preserves OPC's system-record "
            "concept, including placement-date catch-up identified by OPC."
        ),
    )
    print(f"Wrote {len(one_offs)} one-off rows to {paths.OFFICIAL_ONE_OFFS_CSV}")
    print(
        f"Wrote {len(capitalized)} capitalized-interest rows to "
        f"{paths.OFFICIAL_CAPITALIZED_INTEREST_CSV}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
