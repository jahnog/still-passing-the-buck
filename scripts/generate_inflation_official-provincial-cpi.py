#!/usr/bin/env python3
"""Generate the 2007–2015 Santa Fe CPI baseline and official local sensitivities."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import paths
from scripts.data_io import RAW_ROOT, write_meta_sidecar

SANTA_FE_XLS = RAW_ROOT / "santafe" / "ipec_indice-precios-consumidor_2005-01_2013-12.xls"
SANTA_FE_PDF = RAW_ROOT / "santafe" / "ipec_ipc-santa-fe_2017-12_2017-12.pdf"
CABA_XLSX = RAW_ROOT / "caba" / "dgeyc_ipcba-nivel-general_2012-07_2015-12.xlsx"
SAN_LUIS_PDF = RAW_ROOT / "sanluis" / "dpec_ipc-san-luis_2013-01_2016-01.pdf"


def _pdf_text(path: Path) -> str:
    return re.sub(
        r"\s+",
        " ",
        " ".join(page.extract_text() or "" for page in PdfReader(path).pages),
    )


def santa_fe_rates() -> dict[int, float]:
    sheet = pd.read_excel(SANTA_FE_XLS, header=None)
    years = sheet.iloc[4].ffill()
    months = sheet.iloc[5].astype(str).str.strip().str.lower()
    values = sheet.iloc[7]
    december: dict[int, float] = {}
    for year, month, value in zip(years, months, values):
        if month == "diciembre" and not pd.isna(value):
            december[int(year)] = float(value)
    rates = {
        year: 100 * (december[year] / december[year - 1] - 1)
        for year in range(2007, 2014)
    }

    text = _pdf_text(SANTA_FE_PDF)
    required = {
        "2013 December": "2013 Diciembre 82,96",
        "2014 December": "Diciembre 112,15 1,6 35,2",
        "2015 December": "Diciembre 144,36 5,9 28,7",
    }
    normalized = text.replace("\u00a0", " ")
    for label, token in required.items():
        if token not in normalized:
            raise ValueError(f"Santa Fe PDF no longer contains {label} operand token {token!r}")
    rates[2014] = round(100 * (112.15 / 82.96 - 1), 1)
    rates[2015] = round(100 * (144.36 / 112.15 - 1), 1)
    return rates


def caba_rates() -> dict[int, float]:
    sheet = pd.read_excel(CABA_XLSX, sheet_name="Evol_gral_bs_svcios", header=None)
    december: dict[int, float] = {}
    for _, row in sheet.iloc[4:].iterrows():
        try:
            date = pd.Timestamp(row.iloc[0])
            value = float(row.iloc[1])
        except (TypeError, ValueError):
            continue
        if date.month == 12 and 2012 <= date.year <= 2015:
            december[date.year] = value
    if set(december) != {2012, 2013, 2014, 2015}:
        raise ValueError(f"CABA workbook December coverage changed: {sorted(december)}")
    return {
        year: 100 * (december[year] / december[year - 1] - 1)
        for year in range(2013, 2016)
    }


def san_luis_rates() -> dict[int, float]:
    text = _pdf_text(SAN_LUIS_PDF)
    expected_levels = {
        2013: 561.83,
        2014: 780.99,
        2015: 1027.54,
    }
    for value in expected_levels.values():
        token = f"{value:.2f}".replace(".", ",")
        if token not in text:
            raise ValueError(f"San Luis PDF no longer contains December level {token}")
    return {
        year: 100 * (expected_levels[year] / expected_levels[year - 1] - 1)
        for year in (2014, 2015)
    }


def main() -> int:
    santa_fe = santa_fe_rates()
    caba = caba_rates()
    san_luis = san_luis_rates()

    rows: list[dict[str, object]] = []
    for year in range(2007, 2016):
        sf = santa_fe[year]
        alternatives = [sf]
        source_ids = [
            "ipec-santa-fe-cpi-2005-2013"
            if year <= 2013
            else "ipec-santa-fe-cpi-2017-release"
        ]
        if year in caba:
            alternatives.append(caba[year])
            source_ids.append("dgeyc-caba-cpi-2012-2015")
        if year in san_luis:
            alternatives.append(san_luis[year])
            source_ids.append("dpec-san-luis-cpi-2013-2015")
        rows.append(
            {
                "ProvenanceID": f"cpi-santa-fe-{year}",
                "Year": year,
                "Santa_Fe": sf,
                "CABA": caba.get(year),
                "San_Luis": san_luis.get(year),
                "AltAvg": sf,
                "AltMin": min(alternatives),
                "AltMax": max(alternatives),
                "CABA_variant": caba.get(year, sf),
                "San_Luis_variant": san_luis.get(year, sf),
                "SourceIDs": ";".join(source_ids),
                "ExtractionFormula": (
                    "100 * (December index[t] / December index[t-1] - 1); "
                    "AltAvg equals the pre-specified continuous Santa Fe chain"
                ),
                "Uncertainty": (
                    "Santa Fe is the headline; CABA and San Luis are source-defined "
                    "official-local sensitivities only where December levels overlap"
                ),
            }
        )

    result = pd.DataFrame(rows)
    paths.OFFICIAL_PROVINCIAL_CPI_CSV.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(paths.OFFICIAL_PROVINCIAL_CPI_CSV, index=False, float_format="%.9f")
    write_meta_sidecar(
        paths.OFFICIAL_PROVINCIAL_CPI_CSV,
        script=Path(__file__).name,
        sources=[
            str(SANTA_FE_XLS.relative_to(ROOT)),
            str(SANTA_FE_PDF.relative_to(ROOT)),
            str(CABA_XLSX.relative_to(ROOT)),
            str(SAN_LUIS_PDF.relative_to(ROOT)),
        ],
        notes=(
            "Headline AltAvg is the official Santa Fe IPEC December/December chain for "
            "2007-2015. CABA and San Luis are official-local sensitivities where their retained "
            "files provide overlapping December levels. No IPC Congreso or PriceStats estimate "
            "is used."
        ),
    )
    print(f"Wrote {len(result)} rows to {paths.OFFICIAL_PROVINCIAL_CPI_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
