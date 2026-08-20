#!/usr/bin/env python3
"""Generate strict source and row-link registries for official headline corrections."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import paths
from scripts.bcra_importer_debt_bopreal import (
    OUTPUT as BCRA_IMPORTER_DEBT_BOPREAL_OUTPUT,
    SOURCES as BCRA_IMPORTER_DEBT_BOPREAL_SOURCES,
)
from scripts.data_io import RAW_ROOT, file_sha256, latest_raw, write_curated_sidecar
from scripts.hacienda_spn_base_caja import CSV_1993_2006, CSV_2007_2014, CSV_2015_2025
from scripts.official_correction_sources import SOURCES

HACIENDA_SOURCES = (
    (
        "hacienda-spn-base-caja-379-1",
        "SPN base-caja AIF annual values, 1993–2006",
        "2006-12-31",
        (
            "https://infra.datos.gob.ar/catalog/sspm/dataset/379/distribution/379.1/"
            "download/sector-publico-nacional-valores-anuales-93-06.csv"
        ),
        CSV_1993_2006,
    ),
    (
        "hacienda-spn-base-caja-379-2",
        "SPN base-caja AIF annual values, 2007–2014",
        "2014-12-31",
        (
            "https://infra.datos.gob.ar/catalog/sspm/dataset/379/distribution/379.2/"
            "download/sector-publico-nacional-valores-anuales-07-14.csv"
        ),
        CSV_2007_2014,
    ),
    (
        "hacienda-spn-base-caja-379-3",
        "SPN base-caja AIF annual values, 2015–2025",
        "2025-12-31",
        (
            "https://infra.datos.gob.ar/catalog/sspm/dataset/379/distribution/379.3/"
            "download/sector-publico-nacional-valores-anuales-17.csv"
        ),
        CSV_2015_2025,
    ),
)


def _sidecar_retrieved_date(path: Path) -> str:
    sidecar = path.with_name(path.name + ".meta.json")
    if not sidecar.exists():
        raise FileNotFoundError(f"Official raw artifact lacks sidecar: {sidecar}")
    meta = json.loads(sidecar.read_text(encoding="utf-8"))
    timestamp = meta.get("generated_at")
    if not timestamp:
        raise ValueError(f"Official raw sidecar lacks generated_at: {sidecar}")
    return str(timestamp)[:10]


def _source_row(
    source_id: str,
    publisher: str,
    title: str,
    reference_date: str,
    url: str,
    artifact: Path,
) -> dict[str, object]:
    if not artifact.exists():
        raise FileNotFoundError(f"Missing official source artifact: {artifact}")
    return {
        "SourceID": source_id,
        "Publisher": publisher,
        "Title": title,
        "SourceURL": url,
        "ReferenceDate": reference_date,
        "RetrievedDate": _sidecar_retrieved_date(artifact),
        "ArtifactPath": str(artifact.relative_to(ROOT)),
        "ArtifactBytes": artifact.stat().st_size,
        "ArtifactSHA256": file_sha256(artifact),
        "EvidenceClass": "official-published-artifact",
        "ReleaseStatus": "final",
    }


def _hacienda_source_for_year(year: int) -> str:
    if year <= 2006:
        return "hacienda-spn-base-caja-379-1"
    if year <= 2014:
        return "hacienda-spn-base-caja-379-2"
    return "hacienda-spn-base-caja-379-3"


def main() -> int:
    source_rows = [
        _source_row(
            source.source_id,
            source.publisher,
            source.title,
            source.reference_date,
            source.url,
            source.artifact,
        )
        for source in SOURCES
    ]
    for source in BCRA_IMPORTER_DEBT_BOPREAL_SOURCES:
        source_rows.append(
            _source_row(
                source.source_id,
                "Banco Central de la República Argentina",
                source.title,
                source.reference_date,
                source.url,
                source.artifact,
            )
        )
    for source_id, title, date, url, artifact in HACIENDA_SOURCES:
        source_rows.append(
            _source_row(
                source_id,
                "Subsecretaría de Programación Macroeconómica, Ministerio de Economía",
                title,
                date,
                url,
                artifact,
            )
        )
    world_bank_gdp = latest_raw("worldbank", "api_ny-gdp-mktp-cn")
    if world_bank_gdp is None:
        raise FileNotFoundError("Missing raw World Bank NY.GDP.MKTP.CN snapshot")
    # Older World Bank downloaders predate sidecars. Pin this exact committed snapshot here;
    # the registry's hash/size checks provide the missing integrity layer.
    source_rows.append(
        {
            "SourceID": "world-bank-gdp-current-lcu",
            "Publisher": "World Bank",
            "Title": "GDP (current LCU), indicator NY.GDP.MKTP.CN",
            "SourceURL": (
                "https://api.worldbank.org/v2/country/ARG/indicator/NY.GDP.MKTP.CN"
                "?format=json&per_page=20000"
            ),
            "ReferenceDate": "2025-12-31",
            "RetrievedDate": "2026-08-16",
            "ArtifactPath": str(world_bank_gdp.relative_to(ROOT)),
            "ArtifactBytes": world_bank_gdp.stat().st_size,
            "ArtifactSHA256": file_sha256(world_bank_gdp),
            "EvidenceClass": "official-published-api-snapshot",
            "ReleaseStatus": "final",
        }
    )
    sources = pd.DataFrame(source_rows).sort_values("SourceID")
    if sources["SourceID"].duplicated().any():
        raise ValueError("Official source IDs must be unique")
    paths.OFFICIAL_SOURCE_REGISTRY_CSV.parent.mkdir(parents=True, exist_ok=True)
    sources.to_csv(paths.OFFICIAL_SOURCE_REGISTRY_CSV, index=False)
    write_curated_sidecar(
        paths.OFFICIAL_SOURCE_REGISTRY_CSV,
        version="2026-08-17",
        sources=sorted(sources["SourceURL"].astype(str).unique()),
        notes=(
            "Generated from pinned artifacts. Each registry row records the exact repo-relative "
            "artifact, byte count, and SHA-256 used by an official correction."
        ),
    )

    links: list[dict[str, str]] = []
    bcra_operands = pd.read_csv(BCRA_IMPORTER_DEBT_BOPREAL_OUTPUT)
    bcra_output = str(BCRA_IMPORTER_DEBT_BOPREAL_OUTPUT.relative_to(ROOT))
    for _, row in bcra_operands.iterrows():
        links.append(
            {
                "ProvenanceID": str(row["ProvenanceID"]),
                "OutputPath": bcra_output,
                "RowKey": f"ProvenanceID={row['ProvenanceID']}",
                "OutputColumns": (
                    "Measure;Value_USD_M;Baseline_USD_M;ReferenceStock_USD_M;Components"
                ),
                "SourceID": str(row["SourceID"]),
                "SourceLocator": str(row["SourceLocator"]),
                "TransformID": "official-bcra-importer-debt-bopreal-v1",
                "ExtractionFormula": str(row["ExtractionFormula"]),
                "Uncertainty": str(row["Uncertainty"]),
            }
        )
    operands = pd.read_csv(paths.OFFICIAL_FISCAL_OPERANDS_CSV)
    fiscal_output = str(paths.OFFICIAL_ONE_OFFS_CSV.relative_to(ROOT))
    cap_output = str(paths.OFFICIAL_CAPITALIZED_INTEREST_CSV.relative_to(ROOT))
    for _, row in operands.iterrows():
        year = int(row["Year"])
        provenance_id = str(row["ProvenanceID"])
        source_id = str(row["SourceID"])
        if row["CorrectionClass"] == "one-off":
            for linked_source, locator in (
                (source_id, str(row["SourceLocator"])),
                (
                    _hacienda_source_for_year(year),
                    f"year={year}; current-revenue column selected by dataset-379 parser",
                ),
                (
                    "world-bank-gdp-current-lcu",
                    f"country=ARG; indicator=NY.GDP.MKTP.CN; year={year}",
                ),
            ):
                links.append(
                    {
                        "ProvenanceID": provenance_id,
                        "OutputPath": fiscal_output,
                        "RowKey": f"ProvenanceID={provenance_id}",
                        "OutputColumns": (
                            "Amount_ARS_M;CurrentRevenue_ARS_M;NominalGDP_ARS_M;"
                            "Amount_pct_revenues;Amount_pct_GDP"
                        ),
                        "SourceID": linked_source,
                        "SourceLocator": locator,
                        "TransformID": "official-fiscal-one-off-shares-v1",
                        "ExtractionFormula": (
                            "Amount_pct_revenues=Amount_ARS_M/CurrentRevenue_ARS_M*100; "
                            "Amount_pct_GDP=Amount_ARS_M/(NY.GDP.MKTP.CN/1e6)*100"
                        ),
                        "Uncertainty": str(row["Uncertainty"]),
                    }
                )
    cap = pd.read_csv(paths.OFFICIAL_CAPITALIZED_INTEREST_CSV)
    for _, annual in cap.iterrows():
        year = int(annual["Year"])
        provenance_id = str(annual["ProvenanceID"])
        source_ids = str(annual["SourceIDs"]).split(";")
        locators = str(annual["SourceLocators"]).split("; ")
        for source_id, locator in zip(source_ids, locators, strict=True):
            links.append(
                {
                    "ProvenanceID": provenance_id,
                    "OutputPath": cap_output,
                    "RowKey": f"ProvenanceID={provenance_id}",
                    "OutputColumns": (
                        "CapitalizedInterest_ARS_M;CapitalizedInterest_GDP"
                    ),
                    "SourceID": source_id,
                    "SourceLocator": locator,
                    "TransformID": "official-capitalized-interest-ratios-v1",
                    "ExtractionFormula": str(annual["ExtractionFormula"]),
                    "Uncertainty": str(annual["Uncertainty"]),
                }
            )
        for source_id, locator in (
            (
                _hacienda_source_for_year(year),
                f"year={year}; net cash-interest column selected by dataset-379 parser",
            ),
            (
                "world-bank-gdp-current-lcu",
                f"country=ARG; indicator=NY.GDP.MKTP.CN; year={year}",
            ),
        ):
            links.append(
                {
                    "ProvenanceID": provenance_id,
                    "OutputPath": cap_output,
                    "RowKey": f"ProvenanceID={provenance_id}",
                    "OutputColumns": (
                        "CashInterest_ARS_M;NominalGDP_ARS_M;CashInterest_GDP;"
                        "CapitalizedInterest_GDP"
                    ),
                    "SourceID": source_id,
                    "SourceLocator": locator,
                    "TransformID": "official-capitalized-interest-ratios-v1",
                    "ExtractionFormula": str(annual["ExtractionFormula"]),
                    "Uncertainty": str(annual["Uncertainty"]),
                }
            )

    cpi = pd.read_csv(paths.OFFICIAL_PROVINCIAL_CPI_CSV)
    cpi_output = str(paths.OFFICIAL_PROVINCIAL_CPI_CSV.relative_to(ROOT))
    for _, row in cpi.iterrows():
        provenance_id = str(row["ProvenanceID"])
        year = int(row["Year"])
        for source_id in str(row["SourceIDs"]).split(";"):
            links.append(
                {
                    "ProvenanceID": provenance_id,
                    "OutputPath": cpi_output,
                    "RowKey": f"ProvenanceID={provenance_id}",
                    "OutputColumns": (
                        "Santa_Fe;CABA;San_Luis;AltAvg;AltMin;AltMax;"
                        "CABA_variant;San_Luis_variant"
                    ),
                    "SourceID": source_id,
                    "SourceLocator": f"December index levels for {year - 1} and {year}",
                    "TransformID": "official-provincial-cpi-decdec-v1",
                    "ExtractionFormula": str(row["ExtractionFormula"]),
                    "Uncertainty": str(row["Uncertainty"]),
                }
            )

    links_frame = pd.DataFrame(links).sort_values(["OutputPath", "ProvenanceID", "SourceID"])
    links_frame.to_csv(paths.OFFICIAL_ROW_SOURCE_LINKS_CSV, index=False)
    write_curated_sidecar(
        paths.OFFICIAL_ROW_SOURCE_LINKS_CSV,
        version="2026-08-17",
        sources=[
            str(paths.OFFICIAL_SOURCE_REGISTRY_CSV.relative_to(ROOT)),
            bcra_output,
            fiscal_output,
            cap_output,
            cpi_output,
        ],
        notes=(
            "One-to-many links close each generated correction row over its official operand, "
            "denominator, executable transform, and uncertainty statement."
        ),
    )
    print(f"Wrote {len(sources)} sources to {paths.OFFICIAL_SOURCE_REGISTRY_CSV}")
    print(f"Wrote {len(links_frame)} links to {paths.OFFICIAL_ROW_SOURCE_LINKS_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
