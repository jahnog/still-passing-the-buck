#!/usr/bin/env python3
"""Offline provenance checks for headline-affecting corrections and curated inputs."""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import paths
from scripts.data_io import file_sha256
from scripts.hacienda_spn_base_caja import (
    CSV_1993_2006,
    CSV_2007_2014,
    CSV_2015_2025,
    load_spn_base_caja_actuals,
)

TAXONOMY_REQUIRED = {
    "PracticeID",
    "Practice",
    "Period",
    "Bias",
    "Treatment",
    "EvidenceClass",
    "HeadlineAffected",
    "SensitivityVariant",
    "SourceFile",
    "UncertaintyTreatment",
}

TREATMENTS = {
    "Corrected baseline",
    "Sensitivity-only",
    "Documented only",
}

EVIDENCE_CLASSES = {
    "independent replicated series",
    "official revised series",
    "legal/accounting record",
    "market quotation series",
    "historical reconstruction",
    "documented restructuring record",
    "legal/indexation record",
    "official fiscal-document reconstruction",
    "BCRA statistical series",
    "BCRA/official debt reconstruction",
    "documented estimate",
    "alternative official-local index",
    "official instrument accounting",
    "official-statistics record",
    "historical policy record",
    "historical fiscal record",
    "official-workbook-reconstructed",
    "curated-reconstructed",
    "curated-provisional",
    "court/official settlement record",
}

SOURCE_REGISTRY_COLUMNS = {
    "SourceID",
    "Publisher",
    "Title",
    "SourceURL",
    "ReferenceDate",
    "RetrievedDate",
    "ArtifactPath",
    "ArtifactBytes",
    "ArtifactSHA256",
    "EvidenceClass",
    "ReleaseStatus",
}
ROW_LINK_COLUMNS = {
    "ProvenanceID",
    "OutputPath",
    "RowKey",
    "OutputColumns",
    "SourceID",
    "SourceLocator",
    "TransformID",
    "ExtractionFormula",
    "Uncertainty",
}
TRANSFORM_IDS = {
    "official-bcra-importer-debt-bopreal-v1",
    "official-fiscal-one-off-shares-v1",
    "official-capitalized-interest-ratios-v1",
    "official-provincial-cpi-decdec-v1",
}
OFFICIAL_EVIDENCE_CLASSES = {
    "official-published-artifact",
    "official-published-api-snapshot",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

def _nonempty(df: pd.DataFrame, fields: set[str], *, label: str) -> list[str]:
    problems: list[str] = []
    missing = sorted(fields - set(df.columns))
    if missing:
        problems.append(f"{label}: missing columns {missing}")
        return problems
    for field in sorted(fields):
        bad = df[field].isna() | ~df[field].astype(str).str.strip().astype(bool)
        if bad.any():
            rows = ", ".join(str(i) for i in df.index[bad].tolist()[:5])
            problems.append(f"{label}: blank {field!r} at rows {rows}")
    return problems


def _repo_path(value: str) -> Path:
    return ROOT / value.strip()


def validate_taxonomy() -> list[str]:
    df = pd.read_csv(paths.CORRECTION_TAXONOMY_CSV)
    problems = _nonempty(df, TAXONOMY_REQUIRED, label=paths.CORRECTION_TAXONOMY_CSV.name)
    if problems:
        return problems

    ids = df["PracticeID"].astype(int).tolist()
    if len(ids) != len(set(ids)) or any(practice_id <= 0 for practice_id in ids):
        problems.append("correction-taxonomy.csv: PracticeID values must be unique positive integers")

    treatments = set(df["Treatment"].astype(str))
    unknown_treatments = sorted(treatments - TREATMENTS)
    if unknown_treatments:
        problems.append(f"correction-taxonomy.csv: unknown Treatment values {unknown_treatments}")

    evidence = set(df["EvidenceClass"].astype(str))
    unknown_evidence = sorted(evidence - EVIDENCE_CLASSES)
    if unknown_evidence:
        problems.append(f"correction-taxonomy.csv: unknown EvidenceClass values {unknown_evidence}")

    for _, row in df.iterrows():
        headline = str(row["HeadlineAffected"]).strip().lower()
        treatment = str(row["Treatment"]).strip()
        if headline not in {"true", "false"}:
            problems.append(f"taxonomy practice {row['PracticeID']}: HeadlineAffected must be true/false")
        if (treatment == "Corrected baseline") != (headline == "true"):
            problems.append(
                f"taxonomy practice {row['PracticeID']}: headline flag must match corrected-baseline treatment"
            )
        source_file = str(row["SourceFile"]).strip()
        if source_file != "none" and not _repo_path(source_file).exists():
            problems.append(f"taxonomy practice {row['PracticeID']}: SourceFile does not exist: {source_file}")
        if headline == "true" and not str(row["AffectedColumns"]).strip():
            problems.append(f"taxonomy practice {row['PracticeID']}: headline correction needs AffectedColumns")
    return problems


def validate_fiscal_source() -> list[str]:
    """Validate all pinned dataset-379 distributions and complete modern coverage."""
    problems: list[str] = []
    expected = (
        (
            CSV_1993_2006,
            "https://infra.datos.gob.ar/catalog/sspm/dataset/379/distribution/379.1/"
            "download/sector-publico-nacional-valores-anuales-93-06.csv",
        ),
        (
            CSV_2007_2014,
            "https://infra.datos.gob.ar/catalog/sspm/dataset/379/distribution/379.2/"
            "download/sector-publico-nacional-valores-anuales-07-14.csv",
        ),
        (
            CSV_2015_2025,
            "https://infra.datos.gob.ar/catalog/sspm/dataset/379/distribution/379.3/"
            "download/sector-publico-nacional-valores-anuales-17.csv",
        ),
    )
    for artifact, expected_url in expected:
        sidecar_path = artifact.with_name(artifact.name + ".meta.json")
        if not artifact.exists() or not sidecar_path.exists():
            problems.append(f"missing official fiscal source or sidecar: {artifact}")
            continue
        sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
        if sidecar.get("sources") != [expected_url]:
            problems.append(f"{artifact.name}: sidecar must contain the exact official URL")
        output = sidecar.get("output", {})
        if output.get("bytes") != artifact.stat().st_size:
            problems.append(f"{artifact.name}: sidecar byte count does not match")
        if output.get("sha256") != file_sha256(artifact):
            problems.append(f"{artifact.name}: sidecar SHA256 does not match")

    try:
        actuals = load_spn_base_caja_actuals(range(2000, 2026), round_digits=None)
    except (FileNotFoundError, KeyError, RuntimeError, ValueError) as exc:
        problems.append(f"dataset 379 fiscal parsing failed: {exc}")
        return problems
    if set(actuals) != set(range(2000, 2026)):
        problems.append("dataset 379 fiscal source must cover every year 2000..2025")
    return problems


def _strict_columns(frame: pd.DataFrame, expected: set[str], label: str) -> list[str]:
    actual = set(frame.columns)
    if actual == expected:
        return []
    return [
        f"{label}: columns must match strict schema; "
        f"missing={sorted(expected - actual)}, extra={sorted(actual - expected)}"
    ]


def validate_source_registry() -> list[str]:
    problems: list[str] = []
    registry = pd.read_csv(paths.OFFICIAL_SOURCE_REGISTRY_CSV)
    problems.extend(
        _strict_columns(registry, SOURCE_REGISTRY_COLUMNS, paths.OFFICIAL_SOURCE_REGISTRY_CSV.name)
    )
    if problems:
        return problems
    problems.extend(
        _nonempty(registry, SOURCE_REGISTRY_COLUMNS, label=paths.OFFICIAL_SOURCE_REGISTRY_CSV.name)
    )
    if registry["SourceID"].duplicated().any():
        problems.append(
            f"{paths.OFFICIAL_SOURCE_REGISTRY_CSV.name}: SourceID values must be unique"
        )
    if not registry["SourceID"].astype(str).str.match(r"^[a-z0-9][a-z0-9-]+$").all():
        problems.append(
            f"{paths.OFFICIAL_SOURCE_REGISTRY_CSV.name}: SourceID values must be stable slugs"
        )

    for row_number, row in registry.iterrows():
        source_id = str(row["SourceID"])
        url = str(row["SourceURL"])
        if not url.startswith("https://"):
            problems.append(f"source {source_id}: SourceURL must be HTTPS")
        for field in ("ReferenceDate", "RetrievedDate"):
            try:
                date.fromisoformat(str(row[field]))
            except ValueError:
                problems.append(f"source {source_id}: {field} must be ISO YYYY-MM-DD")
        if str(row["EvidenceClass"]) not in OFFICIAL_EVIDENCE_CLASSES:
            problems.append(f"source {source_id}: unsupported official EvidenceClass")
        if str(row["ReleaseStatus"]) != "final":
            problems.append(f"source {source_id}: headline sources must have final release status")

        rel = Path(str(row["ArtifactPath"]))
        if rel.is_absolute() or ".." in rel.parts or rel.parts[:2] != ("data", "raw"):
            problems.append(f"source {source_id}: ArtifactPath must be normalized under data/raw")
            continue
        artifact = (ROOT / rel).resolve()
        raw_root = (ROOT / "data" / "raw").resolve()
        if raw_root not in artifact.parents:
            problems.append(f"source {source_id}: ArtifactPath escapes data/raw")
            continue
        if not artifact.is_file() or artifact.is_symlink():
            problems.append(f"source {source_id}: artifact missing, non-file, or symlinked")
            continue
        digest = str(row["ArtifactSHA256"])
        if not SHA256_RE.fullmatch(digest):
            problems.append(f"source {source_id}: malformed ArtifactSHA256")
        elif file_sha256(artifact) != digest:
            problems.append(f"source {source_id}: artifact SHA256 mismatch")
        if int(row["ArtifactBytes"]) != artifact.stat().st_size:
            problems.append(f"source {source_id}: artifact byte-count mismatch")
    return problems


def _output_rows(path: Path) -> tuple[set[str], set[str]]:
    frame = pd.read_csv(path, dtype=str)
    if "ProvenanceID" not in frame.columns:
        raise ValueError(f"{path}: generated official output lacks ProvenanceID")
    return set(frame["ProvenanceID"].dropna()), set(frame.columns)


def validate_row_source_links() -> list[str]:
    problems: list[str] = []
    registry = pd.read_csv(paths.OFFICIAL_SOURCE_REGISTRY_CSV, dtype=str)
    links = pd.read_csv(paths.OFFICIAL_ROW_SOURCE_LINKS_CSV, dtype=str)
    problems.extend(
        _strict_columns(links, ROW_LINK_COLUMNS, paths.OFFICIAL_ROW_SOURCE_LINKS_CSV.name)
    )
    if problems:
        return problems
    problems.extend(
        _nonempty(links, ROW_LINK_COLUMNS, label=paths.OFFICIAL_ROW_SOURCE_LINKS_CSV.name)
    )
    known_sources = set(registry["SourceID"])
    unknown_sources = sorted(set(links["SourceID"]) - known_sources)
    if unknown_sources:
        problems.append(
            f"{paths.OFFICIAL_ROW_SOURCE_LINKS_CSV.name}: unknown SourceID values {unknown_sources}"
        )
    unknown_transforms = sorted(set(links["TransformID"]) - TRANSFORM_IDS)
    if unknown_transforms:
        problems.append(
            f"{paths.OFFICIAL_ROW_SOURCE_LINKS_CSV.name}: unknown TransformID values {unknown_transforms}"
        )

    output_cache: dict[Path, tuple[set[str], set[str]]] = {}
    linked_by_output: dict[Path, set[str]] = {}
    for _, link in links.iterrows():
        rel = Path(str(link["OutputPath"]))
        if rel.is_absolute() or ".." in rel.parts:
            problems.append(f"row link has non-normalized OutputPath: {rel}")
            continue
        output = ROOT / rel
        if output not in output_cache:
            try:
                output_cache[output] = _output_rows(output)
            except (FileNotFoundError, ValueError) as exc:
                problems.append(str(exc))
                continue
        provenance_ids, columns = output_cache[output]
        provenance_id = str(link["ProvenanceID"])
        if provenance_id not in provenance_ids:
            problems.append(f"row link orphan: {provenance_id} not found in {rel}")
        if str(link["RowKey"]) != f"ProvenanceID={provenance_id}":
            problems.append(f"row link {provenance_id}: RowKey must resolve by ProvenanceID")
        unknown_columns = set(str(link["OutputColumns"]).split(";")) - columns
        if unknown_columns:
            problems.append(
                f"row link {provenance_id}: unknown output columns {sorted(unknown_columns)}"
            )
        linked_by_output.setdefault(output, set()).add(provenance_id)

    required_outputs = (
        paths.OFFICIAL_ONE_OFFS_CSV,
        paths.OFFICIAL_CAPITALIZED_INTEREST_CSV,
        paths.OFFICIAL_PROVINCIAL_CPI_CSV,
    )
    for output in required_outputs:
        try:
            provenance_ids, _ = _output_rows(output)
        except (FileNotFoundError, ValueError) as exc:
            problems.append(str(exc))
            continue
        unlinked = sorted(provenance_ids - linked_by_output.get(output, set()))
        if unlinked:
            problems.append(f"{output.name}: unlinked official rows {unlinked}")
    return problems


def validate_removed_models_absent() -> list[str]:
    """Reject the four F-05 models in source data or generated headline columns."""
    problems: list[str] = []
    removed_paths = (
        ROOT / "data/provided/fiscal-one-offs.csv",
        ROOT / "data/provided/alt-cpi-2007-2015.csv",
        ROOT / "data/provided/contingent-liabilities.csv",
        ROOT / "data/provided/default-window-interest.csv",
    )
    for path in removed_paths:
        if path.exists():
            problems.append(f"removed F-05 model file still exists: {path.relative_to(ROOT)}")

    operand_text = paths.OFFICIAL_FISCAL_OPERANDS_CSV.read_text(encoding="utf-8").lower()
    blocked = ("law 26.476", "dolar-soja", "dólar-soja", "paris club", "unpaid interest")
    for token in blocked:
        if token in operand_text:
            problems.append(f"official fiscal operands contain removed model token {token!r}")
    one_offs = pd.read_csv(paths.OFFICIAL_ONE_OFFS_CSV)
    if set(one_offs["Year"].astype(int)) & {2022, 2023}:
        problems.append("official one-offs contain removed 2022-2023 timing-model rows")

    capitalized = pd.read_csv(paths.OFFICIAL_CAPITALIZED_INTEREST_CSV, nrows=1)
    obsolete_interest_columns = {"InterestPaid_GDP", "AccruedUnpaidInterest_GDP"}
    present = sorted(obsolete_interest_columns & set(capitalized.columns))
    if present:
        problems.append(f"capitalized-interest output retains obsolete model names: {present}")

    fpi = pd.read_csv(paths.FPI_FISCAL_CSV, nrows=1)
    forbidden_columns = {
        "Debt_GDP_contingent",
        "Debt_Exports_contingent",
        "Result_DebtServ_accrual",
    }
    forbidden_present = sorted(forbidden_columns & set(fpi.columns))
    if forbidden_present:
        problems.append(f"FPI output retains removed-model memo columns: {forbidden_present}")
    return problems


def main() -> int:
    problems = (
        validate_taxonomy()
        + validate_fiscal_source()
        + validate_source_registry()
        + validate_row_source_links()
        + validate_removed_models_absent()
    )
    if problems:
        print("Provenance validation failed:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print("Provenance validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
