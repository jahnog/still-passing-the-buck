#!/usr/bin/env python3
"""Download and validate Secretaría de Hacienda SPN base-caja annual series (2000-2025).

Source: datos.gob.ar SSPM dataset 379 "Esquema Ahorro-Inversión-Financiamiento. Sector
Público Nacional. Base Caja." — the official Subsecretaría de Programación Macroeconómica
publication of the SPN cash-basis AIF scheme.

Two CSV files cover 1993-2006 and 2007-2014 respectively; a third CSV (labeled "2017")
provides 2015-2025 data with the same concept. Cross-validated against the Hacienda IMIG
annual files (confirmed exact match for 2017 and 2018).

Validation gate: primary result and interest for 2018 from datos.gob.ar must reproduce the
IMIG 2018 annual file within 0.1% (primary) / 0.5% (interest). If this gate fails, the
dataset has been revised and the base-caja sourcing in generate_fiscal_fpi-fiscal.py (which
parses these same raw CSVs) must be reviewed.

Ratios computed:
    ratio1 = superavit_primario / ingresos_corrientes   (= Result_Revenue in the FPI)
    ratio2 = superavit_primario / intereses_netos       (= Result_DebtServ in the FPI)
    where intereses_netos = superavit_primario - resultado_financiero

Outputs (saved to data/raw/hacienda/):
    spn-base-caja_valores-anuales_1993_2006.csv
    spn-base-caja_valores-anuales_2007_2014.csv
    spn-base-caja_valores-anuales_2015_2025_raw.csv
    imig-anual_2017.xlsx
    imig-anual_2018.xlsx

Prints the computed base-caja ratio entries for 2000-2025 to stdout for inspection. These
values are NOT hardcoded: generate_fiscal_fpi-fiscal.py parses them at generation time from the
committed raw CSVs via scripts/hacienda_spn_base_caja.load_spn_base_caja_ratios(). This script
just (re)downloads and re-validates the raw inputs.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_io import RAW_ROOT, atomic_download, write_meta_sidecar
from scripts.hacienda_spn_base_caja import (
    imig_totals,
    load_spn_base_caja_actuals,
    load_spn_base_caja_ratios,
    validate_against_imig,
)

HACIENDA_DIR = RAW_ROOT / "hacienda"

# datos.gob.ar SSPM dataset 379 — SPN base-caja annual series
URL_93_06 = (
    "https://infra.datos.gob.ar/catalog/sspm/dataset/379/distribution/379.1/download/"
    "sector-publico-nacional-valores-anuales-93-06.csv"
)
URL_07_14 = (
    "https://infra.datos.gob.ar/catalog/sspm/dataset/379/distribution/379.2/download/"
    "sector-publico-nacional-valores-anuales-07-14.csv"
)
URL_15_25 = (
    "https://infra.datos.gob.ar/catalog/sspm/dataset/379/distribution/379.3/download/"
    "sector-publico-nacional-valores-anuales-17.csv"
)
# Hacienda IMIG annual files (for cross-validation)
URL_IMIG_2017 = "https://www.argentina.gob.ar/sites/default/files/imig-2017.xlsx"
URL_IMIG_2018 = "https://www.argentina.gob.ar/sites/default/files/imig-2018.xlsx"

DEST_93_06   = HACIENDA_DIR / "spn-base-caja_valores-anuales_1993_2006.csv"
DEST_07_14   = HACIENDA_DIR / "spn-base-caja_valores-anuales_2007_2014.csv"
DEST_15_25   = HACIENDA_DIR / "spn-base-caja_valores-anuales_2015_2025_raw.csv"
DEST_IMIG_17 = HACIENDA_DIR / "imig-anual_2017.xlsx"
DEST_IMIG_18 = HACIENDA_DIR / "imig-anual_2018.xlsx"

SOURCE_URLS = [
    ("datos.gob.ar SSPM dataset 379 distribution 379.1", URL_93_06),
    ("datos.gob.ar SSPM dataset 379 distribution 379.2", URL_07_14),
    ("datos.gob.ar SSPM dataset 379 distribution 379.3", URL_15_25),
    ("Hacienda IMIG anual 2017", URL_IMIG_2017),
    ("Hacienda IMIG anual 2018", URL_IMIG_2018),
]


def main() -> int:
    HACIENDA_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Download raw files
    print("Downloading datos.gob.ar SPN base-caja annual CSVs...")
    atomic_download(URL_93_06, DEST_93_06, min_size=1_000)
    print(f"  Wrote {DEST_93_06.name}")
    atomic_download(URL_07_14, DEST_07_14, min_size=1_000)
    print(f"  Wrote {DEST_07_14.name}")
    atomic_download(URL_15_25, DEST_15_25, min_size=1_000)
    print(f"  Wrote {DEST_15_25.name}")

    print("Downloading Hacienda IMIG annual xlsx files (2017, 2018)...")
    atomic_download(URL_IMIG_2017, DEST_IMIG_17, min_size=5_000)
    print(f"  Wrote {DEST_IMIG_17.name}")
    atomic_download(URL_IMIG_2018, DEST_IMIG_18, min_size=5_000)
    print(f"  Wrote {DEST_IMIG_18.name}")

    # 2. Meta sidecars
    for dest in [DEST_93_06, DEST_07_14, DEST_15_25]:
        write_meta_sidecar(
            dest,
            script=Path(__file__).name,
            sources=[URL_93_06 if "1993" in dest.name else URL_07_14 if "2007" in dest.name else URL_15_25],
            notes="datos.gob.ar SSPM dataset 379 — SPN base-caja AIF scheme annual values",
        )
    for dest in [DEST_IMIG_17, DEST_IMIG_18]:
        yr = dest.name.replace("imig-anual_", "").replace(".xlsx", "")
        write_meta_sidecar(
            dest,
            script=Path(__file__).name,
            sources=[URL_IMIG_2017 if yr == "2017" else URL_IMIG_2018],
            notes=f"Hacienda IMIG {yr} annual file — used for cross-validation of datos.gob.ar source",
        )

    # 3. Compute official operands and ratios for the complete modern span.
    print("\nComputing SPN base-caja operands and ratios for 2000-2025...")
    all_actuals = load_spn_base_caja_actuals(range(2000, 2026), round_digits=None)
    all_ratios = load_spn_base_caja_ratios(range(2000, 2026), round_digits=None)

    # 4. Validate against IMIG 2018 annual
    print("\nCross-validating 2018 against Hacienda IMIG 2018 annual file...")
    imig18 = imig_totals(DEST_IMIG_18)
    err18 = validate_against_imig(all_ratios, imig18, year=2018)
    print(f"  Validation PASSED: 2018 primary {all_actuals[2018].primary_result:,.1f} vs "
          f"IMIG {imig18['primary']:,.1f} (err={err18:.4%})")
    imig17 = imig_totals(DEST_IMIG_17)
    if "primary" in imig17 and 2017 in all_ratios:
        err17 = abs(all_ratios[2017][2] - imig17["primary"]) / abs(imig17["primary"])
        print(f"  Cross-check 2017: datos={all_ratios[2017][2]:,.1f} vs IMIG={imig17['primary']:,.1f} (err={err17:.4%})")

    # 5. Print the base-caja ratio entries for 2000-2025 (inspection only — parsed live by the
    #    generator from these same raw CSVs, not copied into Python).
    print("\n# SPN base-caja ratios for 2000-2025 (parsed live by generate_fiscal_fpi-fiscal.py):")
    print("# Source: datos.gob.ar SSPM dataset 379 (SPN base-caja AIF) + Hacienda IMIG 2017/2018")
    print("# ratio1 = superavit_primario / ingresos_corrientes")
    print("# ratio2 = superavit_primario / (superavit_primario - resultado_financiero)")
    print("base_caja_ratios_2000_2025 = {")
    for yr in sorted(all_ratios):
        r1v, r2v, prim = all_ratios[yr]
        actual = all_actuals[yr]
        print(
            f"    {yr}: ({r1v:+.4f}, {r2v:+.4f}),  "
            f"# primary={prim:,.1f}, interest={actual.interest_measure:,.1f}, "
            f"current_revenue={actual.current_revenue:,.1f} M$"
        )
    print("}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
