#!/usr/bin/env python3
"""Generate official 2022–25 importer-debt increase and BOPREAL residual operands."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.bcra_importer_debt_bopreal import (
    BOPREAL_SOURCE,
    IMPORTER_DEBT_SOURCE,
    OUTPUT,
    build_output,
)
from scripts.data_io import write_meta_sidecar


def main() -> int:
    for source in (IMPORTER_DEBT_SOURCE, BOPREAL_SOURCE):
        if not source.artifact.exists():
            raise FileNotFoundError(
                f"Missing BCRA raw artifact {source.artifact}; "
                "run scripts/download_bcra_importer-debt-bopreal.py"
            )

    output = build_output(
        IMPORTER_DEBT_SOURCE.artifact.read_bytes(),
        BOPREAL_SOURCE.artifact.read_bytes(),
    )
    if output["Year"].tolist() != [2022, 2023, 2024, 2025]:
        raise ValueError("BCRA importer-debt/BOPREAL output must cover exactly 2022–2025")
    if output["ProvenanceID"].duplicated().any():
        raise ValueError("BCRA importer-debt/BOPREAL provenance IDs must be unique")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT, index=False)
    write_meta_sidecar(
        OUTPUT,
        script=Path(__file__).name,
        sources=[
            str(IMPORTER_DEBT_SOURCE.artifact.relative_to(ROOT)),
            str(BOPREAL_SOURCE.artifact.relative_to(ROOT)),
        ],
        notes=(
            "2022–23 are cumulative BCRA importer-debt stock increases from the common "
            "December-2021 baseline. 2024–25 are audited BOPREAL Series 1–3 residual values; "
            "mixed-purpose Series 4 is excluded."
        ),
    )
    print(f"Wrote {len(output)} rows to {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
