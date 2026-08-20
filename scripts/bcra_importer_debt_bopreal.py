"""Official BCRA sources and parsers for the paired importer-debt/BOPREAL series."""

from __future__ import annotations

import io
import re
from dataclasses import dataclass
from pathlib import Path
from zipfile import BadZipFile, ZipFile

import pandas as pd
from pypdf import PdfReader

from scripts.data_io import RAW_ROOT, processed_path

BCRA_PUBLISHER = "Banco Central de la República Argentina"


@dataclass(frozen=True)
class BCRASource:
    source_id: str
    title: str
    reference_date: str
    url: str
    artifact: Path
    min_size: int
    release_status: str = "final"


IMPORTER_DEBT_SOURCE = BCRASource(
    source_id="bcra-private-external-debt-raype",
    title="Anexo de deuda externa privada — Relevamiento de Activos y Pasivos Externos",
    reference_date="2026-03-31",
    url=(
        "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/informes/"
        "ANEXODEUDAPRIVADA_6401.xlsx"
    ),
    artifact=(
        RAW_ROOT
        / "bcra"
        / "estadisticas_anexo-deuda-externa-privada-raype_2017-12_2026-03.xlsx"
    ),
    min_size=1_000_000,
)

BOPREAL_SOURCE = BCRASource(
    source_id="bcra-financial-statements-2025",
    title="Estados Contables al 31 de diciembre de 2025",
    reference_date="2025-12-31",
    url=(
        "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/informes/"
        "estados-contables-2025.pdf"
    ),
    artifact=RAW_ROOT / "bcra" / "publicaciones_estados-contables_2025-01_2025-12.pdf",
    min_size=100_000,
)

SOURCES = (IMPORTER_DEBT_SOURCE, BOPREAL_SOURCE)

OUTPUT = processed_path(
    "fiscal",
    "bcra-importer-debt-bopreal",
    "2022-01",
    "2025-12",
)

IMPORT_OPERATIONS = {
    "Deuda de importaciones de bienes",
    "Deuda de importaciones de servicios",
}
YEAR_END_PERIODS = (202112, 202212, 202312)
BASELINE_PERIOD = 202112
MEASURE_BY_YEAR = {
    2022: "ImporterDebtIncrease",
    2023: "ImporterDebtIncrease",
    2024: "BOPREALResidual",
    2025: "BOPREALResidual",
}
EXPECTED_VALUES_USD_M = {
    2022: 9_975.820933,
    2023: 28_219.350873,
    2024: 9_147.038,
    2025: 6_817.813,
}


def validate_importer_debt_xlsx(content: bytes) -> None:
    """Reject soft-404s and workbooks lacking the two machine-readable source tables."""
    if len(content) < IMPORTER_DEBT_SOURCE.min_size:
        raise RuntimeError(
            f"BCRA importer-debt workbook is too small: {len(content)} bytes"
        )
    if not content.startswith(b"PK\x03\x04"):
        preview = content[:120].decode("utf-8", errors="replace").replace("\n", " ")
        raise RuntimeError(f"BCRA importer-debt response is not XLSX: {preview!r}")
    try:
        workbook = pd.ExcelFile(io.BytesIO(content))
    except (BadZipFile, ValueError) as exc:
        raise RuntimeError("BCRA importer-debt workbook cannot be opened") from exc
    required = {"Tabla de datos I", "Tabla de datos II"}
    missing = required - set(workbook.sheet_names)
    if missing:
        raise RuntimeError(
            f"BCRA importer-debt workbook lacks required sheets: {sorted(missing)}"
        )


def validate_bopreal_pdf(content: bytes) -> str:
    """Reject soft-404s and PDFs that do not contain the audited BOPREAL note."""
    if len(content) < BOPREAL_SOURCE.min_size:
        raise RuntimeError(f"BCRA financial-statements PDF is too small: {len(content)} bytes")
    if not content.startswith(b"%PDF"):
        preview = content[:120].decode("utf-8", errors="replace").replace("\n", " ")
        raise RuntimeError(f"BCRA financial-statements response is not PDF: {preview!r}")
    text = _pdf_text(content)
    required = ("4.15 Títulos emitidos por el BCRA", "BOPREAL", "Valor Residual")
    missing = [token for token in required if token not in text]
    if missing:
        raise RuntimeError(f"BCRA financial-statements PDF lacks Note 4.15 tokens: {missing}")
    return text


def _normalise_columns(frame: pd.DataFrame) -> pd.DataFrame:
    normalised = frame.copy()
    normalised.columns = [
        re.sub(r"\s+", " ", str(column)).strip().rstrip(".") for column in normalised.columns
    ]
    return normalised


def _parse_importer_debt_sheet(raw: bytes, sheet_name: str) -> dict[int, float]:
    frame = pd.read_excel(io.BytesIO(raw), sheet_name=sheet_name, header=6)
    frame = _normalise_columns(frame)
    required = {"Periodo", "Tipo de operación", "Valor nominal residual final"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"{sheet_name}: missing required columns {sorted(missing)}")

    periods = pd.to_numeric(frame["Periodo"], errors="coerce")
    values = pd.to_numeric(frame["Valor nominal residual final"], errors="coerce")
    operations = frame["Tipo de operación"].astype(str).str.strip()
    selected = pd.DataFrame(
        {"Period": periods, "Operation": operations, "Value": values}
    )
    selected = selected[
        selected["Period"].isin(YEAR_END_PERIODS)
        & selected["Operation"].isin(IMPORT_OPERATIONS)
    ]
    if selected.empty:
        raise ValueError(f"{sheet_name}: no importer-debt rows matched the specified filters")
    if selected["Value"].isna().any():
        raise ValueError(f"{sheet_name}: importer-debt rows contain non-numeric residual values")

    totals = selected.groupby("Period", observed=True)["Value"].sum()
    missing_periods = set(YEAR_END_PERIODS) - set(totals.index.astype(int))
    if missing_periods:
        raise ValueError(f"{sheet_name}: missing periods {sorted(missing_periods)}")
    return {int(period): float(totals.loc[period]) for period in YEAR_END_PERIODS}


def parse_importer_debt_stocks(raw: bytes) -> dict[int, float]:
    """Return year-end importer debt stocks in USD millions, cross-checked across two tables."""
    validate_importer_debt_xlsx(raw)
    primary = _parse_importer_debt_sheet(raw, "Tabla de datos I")
    cross_check = _parse_importer_debt_sheet(raw, "Tabla de datos II")
    for period in YEAR_END_PERIODS:
        if abs(primary[period] - cross_check[period]) > 1e-6:
            raise ValueError(
                "BCRA importer-debt workbook tables disagree for "
                f"{period}: {primary[period]} vs {cross_check[period]}"
            )
        if primary[period] < 0:
            raise ValueError(f"BCRA importer-debt stock is negative for {period}")
    return primary


def importer_debt_increases(raw: bytes) -> dict[int, float]:
    """Return cumulative 2022–23 stock increases from the common December-2021 baseline."""
    stocks = parse_importer_debt_stocks(raw)
    baseline = stocks[BASELINE_PERIOD]
    increases = {
        2022: stocks[202212] - baseline,
        2023: stocks[202312] - baseline,
    }
    if any(value < 0 for value in increases.values()):
        raise ValueError(f"Importer-debt increase became negative: {increases}")
    return increases


def _pdf_text(raw: bytes) -> str:
    return re.sub(
        r"\s+",
        " ",
        " ".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(raw)).pages),
    ).strip()


def _year_block(text: str, year: int) -> str:
    marker = f"Monto en pesos al 31/12/{str(year)[-2:]}"
    start = text.find(marker)
    if start < 0:
        raise ValueError(f"BCRA Note 4.15 lacks marker {marker!r}")
    data_start = start + len(marker)
    next_marker = text.find("Monto en pesos al 31/12/", data_start)
    if next_marker < 0:
        next_marker = text.find("(*) Incluye", data_start)
    if next_marker < 0:
        next_marker = min(len(text), start + 1_200)
    return text[start:next_marker]


def _series_residuals(block: str, year: int) -> dict[int, float]:
    """Parse `Serie N <nominal> <residual> <ARS amount>` rows; USD fields are thousands."""
    matches = re.findall(
        r"Serie\s+([1-4])\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)",
        block,
    )
    if not matches:
        raise ValueError(f"BCRA Note 4.15 contains no parseable Series rows for {year}")
    residuals: dict[int, float] = {}
    for series, _nominal, residual, _pesos in matches:
        series_number = int(series)
        residuals[series_number] = float(residual.replace(".", "")) / 1_000
    return residuals


def parse_bopreal_residuals(raw: bytes) -> tuple[dict[int, float], dict[int, dict[int, float]]]:
    """Return importer-focused Series 1–3 residuals in USD millions for 2024 and 2025."""
    text = validate_bopreal_pdf(raw)
    components: dict[int, dict[int, float]] = {}
    for year in (2025, 2024):
        components[year] = _series_residuals(_year_block(text, year), year)

    required = {2024: {1, 2, 3}, 2025: {1, 3}}
    for year, series in required.items():
        missing = series - set(components[year])
        if missing:
            raise ValueError(f"BCRA Note 4.15 lacks Series {sorted(missing)} for {year}")
    if 4 not in components[2025]:
        raise ValueError("BCRA Note 4.15 lacks Series 4 needed to enforce its exclusion")

    totals = {
        year: sum(components[year].get(series, 0.0) for series in (1, 2, 3))
        for year in (2024, 2025)
    }
    if any(value <= 0 for value in totals.values()):
        raise ValueError(f"BOPREAL residual total is not positive: {totals}")
    return totals, components


def build_output(importer_raw: bytes, bopreal_raw: bytes) -> pd.DataFrame:
    """Build the four provenance-rich annual operands consumed by the fiscal pipeline."""
    stocks = parse_importer_debt_stocks(importer_raw)
    increases = {
        2022: stocks[202212] - stocks[BASELINE_PERIOD],
        2023: stocks[202312] - stocks[BASELINE_PERIOD],
    }
    if any(value < 0 for value in increases.values()):
        raise ValueError(f"Importer-debt increase became negative: {increases}")
    bopreal, components = parse_bopreal_residuals(bopreal_raw)
    extracted = {**increases, **bopreal}
    for year, expected in EXPECTED_VALUES_USD_M.items():
        tolerance = 1.0 if year in (2022, 2023) else 0.001
        if abs(extracted[year] - expected) > tolerance:
            raise ValueError(
                f"BCRA operand drift for {year}: extracted {extracted[year]:.6f}, "
                f"expected {expected:.6f} ± {tolerance:.3f} USDm"
            )

    rows = [
        {
            "Year": year,
            "Measure": MEASURE_BY_YEAR[year],
            "Value_USD_M": round(increases[year], 6),
            "Baseline_USD_M": round(stocks[BASELINE_PERIOD], 6),
            "ReferenceStock_USD_M": round(stocks[year * 100 + 12], 6),
            "Components": "imported goods debt + imported services debt",
            "ProvenanceID": f"bcra-importer-debt-increase-{year}",
            "SourceID": IMPORTER_DEBT_SOURCE.source_id,
            "SourceLocator": (
                "sheets=Tabla de datos I,Tabla de datos II; "
                f"periods=202112,{year}12; operations=Deuda de importaciones de bienes,"
                "Deuda de importaciones de servicios"
            ),
            "ExtractionFormula": (
                f"ImporterDebtIncrease_{year}=ImporterDebtStock_{year}12"
                "-ImporterDebtStock_202112"
            ),
            "Uncertainty": (
                "deterministic extraction from the pinned BCRA workbook; "
                "source series may be revised in later releases"
            ),
        }
        for year in (2022, 2023)
    ]
    for year in (2024, 2025):
        included = [series for series in (1, 2, 3) if series in components[year]]
        rows.append(
            {
                "Year": year,
                "Measure": MEASURE_BY_YEAR[year],
                "Value_USD_M": round(bopreal[year], 6),
                "Baseline_USD_M": pd.NA,
                "ReferenceStock_USD_M": round(bopreal[year], 6),
                "Components": "+".join(f"Series {series}" for series in included),
                "ProvenanceID": f"bcra-bopreal-residual-{year}",
                "SourceID": BOPREAL_SOURCE.source_id,
                "SourceLocator": f"Note 4.15; Valor Residual; 31/12/{str(year)[-2:]}",
                "ExtractionFormula": (
                    "BOPREALResidual=sum(ValorResidual Series 1-3)/1000; "
                    "Series 4 excluded"
                ),
                "Uncertainty": (
                    "exact audited residual values; Series 4 excluded because it also covers "
                    "dividends and related-party obligations"
                ),
            }
        )
    return pd.DataFrame(rows)
