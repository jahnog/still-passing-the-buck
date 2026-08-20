"""Central paths for notebook inputs and validators."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROVIDED = ROOT / "data" / "provided"
PROCESSED = ROOT / "data" / "processed"

INDICATORS_CSV = (
    PROCESSED / "indicators" / "converted_indicators_wdi-argentina_1960-01_2025-12.csv"
)
INDICATORS_GZ = (
    PROCESSED / "indicators" / "converted_indicators_wdi-argentina_1960-01_2025-12.csv.gz"
)
DATA_A_1999_XLSX = PROVIDED / "data_a_1999.xlsx"
DATA_QUALITY_FLAGS_CSV = PROVIDED / "data-quality-flags.csv"
CORRECTION_TAXONOMY_CSV = PROVIDED / "correction-taxonomy.csv"
DEFAULT_ADJUSTMENTS_CSV = PROVIDED / "fiscal-default-adjustments.csv"
OFFICIAL_FISCAL_OPERANDS_CSV = PROVIDED / "official-fiscal-correction-operands.csv"
OFFICIAL_SOURCE_REGISTRY_CSV = (
    PROCESSED / "provenance" / "converted_provenance_source-registry.csv"
)
OFFICIAL_ROW_SOURCE_LINKS_CSV = (
    PROCESSED / "provenance" / "converted_provenance_row-source-links.csv"
)
PARALLEL_FX_HISTORICAL_CSV = PROVIDED / "parallel-fx-historical.csv"
US_REAL_YIELD_CSV = (
    PROCESSED / "interest" / "converted_interest_us-real-yield-10y_1998-01_2025-12.csv"
)
IPCBA_VS_INDEC_CSV = PROVIDED / "ipcba-vs-indec.csv"
BCRA_QF_HISTORICAL_CSV = PROVIDED / "bcra-quasi-fiscal-historical.csv"
BCRA_QF_ANCHORS_CSV = PROVIDED / "bcra-quasi-fiscal-anchors.csv"
# Sensitivity-only inputs (section 9.7-9.9): never consumed by the corrected headline baseline.
RESTRUCTURING_2005_CSV = PROVIDED / "restructuring-2005-sensitivity.csv"

INTEREST_CSV = PROCESSED / "interest" / "converted_interest_wb-ids-arg_1958-01_2025-12.csv"
PARALLEL_CEPO_CSV = PROCESSED / "exchange" / "converted_exchange_parallel-cepo_2012-01_2025-12.csv"
PAPER_DEVALUATION_CSV = PROCESSED / "exchange" / "converted_exchange_paper-devaluation_1853-01_1999-12.csv"
DEC_DEC_MODERN_CSV = PROCESSED / "exchange" / "converted_exchange_dec-dec_1999-01_2025-12.csv"
HISTORICAL_CMPI_CSV = PROCESSED / "historical" / "converted_historical_historical-cmpi_1852-01_1963-12.csv"
HIST_EXCEL_ANNUAL_CSV = (
    PROCESSED / "historical" / "converted_historical_data-a-1999-excel_1853-01_1963-12.csv"
)
BCRA_QUASI_FISCAL_CSV = PROCESSED / "fiscal" / "converted_fiscal_bcra-quasi-fiscal_2001-01_2025-12.csv"
BCRA_IMPORTER_DEBT_BOPREAL_CSV = (
    PROCESSED
    / "fiscal"
    / "converted_fiscal_bcra-importer-debt-bopreal_2022-01_2025-12.csv"
)
FPI_FISCAL_CSV = PROCESSED / "fiscal" / "converted_fiscal_fpi-fiscal_1853-01_2025-12.csv"
OFFICIAL_ONE_OFFS_CSV = (
    PROCESSED / "fiscal" / "converted_fiscal_official-one-offs_2009-01_2024-12.csv"
)
OFFICIAL_CAPITALIZED_INTEREST_CSV = (
    PROCESSED
    / "fiscal"
    / "converted_fiscal_official-capitalized-interest_2024-01_2025-12.csv"
)
OFFICIAL_PROVINCIAL_CPI_CSV = (
    PROCESSED
    / "inflation"
    / "converted_inflation_official-provincial-cpi_2007-01_2015-12.csv"
)
# Notebook/validator compatibility name for the official Santa Fe baseline.
ALT_CPI_CSV = OFFICIAL_PROVINCIAL_CPI_CSV
DENOMINATOR_NEUTRAL_CSV = (
    PROCESSED / "fiscal" / "converted_fiscal_denominator-neutral_1960-01_2025-12.csv"
)


