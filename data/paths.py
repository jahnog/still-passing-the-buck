"""Central paths for notebook inputs and validators."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROVIDED = ROOT / "data" / "provided"
PROCESSED = ROOT / "data" / "processed"

INDICATORS_CSV = PROVIDED / "Indicators.csv"
INDICATORS_GZ = PROVIDED / "Indicators.csv.gz"
DATA_A_2018_XLSX = PROVIDED / "data_a_2018.xlsx"
ALT_CPI_CSV = PROVIDED / "alt-cpi-2007-2015.csv"
DATA_QUALITY_FLAGS_CSV = PROVIDED / "data-quality-flags.csv"
DEFAULT_ADJUSTMENTS_CSV = PROVIDED / "fiscal-default-adjustments.csv"
FISCAL_ONE_OFFS_CSV = PROVIDED / "fiscal-one-offs.csv"
CEPO_FX_SHARES_CSV = PROVIDED / "cepo-fx-shares.csv"
CONTINGENT_LIABILITIES_CSV = PROVIDED / "contingent-liabilities.csv"
PARALLEL_FX_HISTORICAL_CSV = PROVIDED / "parallel-fx-historical.csv"
US_REAL_YIELD_CSV = PROVIDED / "us-real-yield-10y.csv"
IPCBA_VS_INDEC_CSV = PROVIDED / "ipcba-vs-indec.csv"
BCRA_QF_HISTORICAL_CSV = PROVIDED / "bcra-quasi-fiscal-historical.csv"

INTEREST_CSV = PROCESSED / "interest" / "converted_interest_wb-ids-arg_1958-01_2025-12.csv"
PARALLEL_CEPO_CSV = PROCESSED / "exchange" / "converted_exchange_parallel-cepo_2012-01_2025-12.csv"
PAPER_DEVALUATION_CSV = PROCESSED / "exchange" / "converted_exchange_paper-devaluation_1853-01_1999-12.csv"
BCRA_DEC_DEC_CSV = PROCESSED / "exchange" / "converted_exchange_bcra-dec-dec_1989-01_1995-12.csv"
DEC_DEC_MODERN_CSV = PROCESSED / "exchange" / "converted_exchange_dec-dec_1999-01_2025-12.csv"
HISTORICAL_CMPI_CSV = PROCESSED / "historical" / "converted_historical_historical-cmpi_1852-01_1963-12.csv"
HIST_EXCEL_ANNUAL_CSV = (
    PROCESSED / "historical" / "converted_historical_data-a-2018-excel_1853-01_1963-12.csv"
)
BCRA_QUASI_FISCAL_CSV = PROCESSED / "fiscal" / "converted_fiscal_bcra-quasi-fiscal_2001-01_2025-12.csv"
FPI_FISCAL_CSV = PROCESSED / "fiscal" / "converted_fiscal_fpi-fiscal_1853-01_2025-12.csv"

# Legacy wide WDI Argentina extract (generated from raw WDI zip until fully migrated)
WIDE_WDI_CSV = ROOT / "WDIData2.csv"
