from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import cmpi_core

# --- Appendix D <-> code identity ------------------------------------------


def test_appendix_d_states_single_pool_size_for_all_components() -> None:
    """Regression guard for the O_v = 170 leftover.

    Appendix D once claimed primary-result components ranked only 170
    innovations while also stating that the 1861-63 interpolation gives every
    FPI component 173. The interpolation in cmpi_core.interpolate_fpi_ratio_gaps
    makes 173 correct for every component; the contradiction must not return.
    """
    paper = (ROOT / "paper" / "paper.md").read_text(encoding="utf-8")
    assert "O_v=170" not in paper.replace(" ", "")
    assert "$O_v=173$" in paper


def test_appendix_d_documents_operational_percentile_formula() -> None:
    """The operational score is R = (rank_average - 1) / n (cmpi_core._percentile_assign).

    Appendix D must present that rank form, not only the original
    R = (O_v - o) / O position form.
    """
    paper = (ROOT / "paper" / "paper.md").read_text(encoding="utf-8")
    compact = paper.replace(" ", "").replace("\\frac", "")
    assert "{r_{v,t}-1}{O_v}" in compact
    assert "(O_v-o_{v,t})/O_v" in compact


def test_percentile_assign_matches_appendix_d_algebra() -> None:
    df = pd.DataFrame(
        {"x": [10.0, 30.0, 20.0]},
        index=pd.Index([2001, 2002, 2003], name="Year"),
    )
    out = cmpi_core._percentile_assign(df.copy(), "x", ascending=True)
    # ascending=True: 10 is worst (rank 1 -> Pos 0), 30 is best ((n-1)/n).
    assert out["xPos"].tolist() == pytest.approx([0.0, 2 / 3, 1 / 3])


def test_percentile_assign_average_ties_share_slots() -> None:
    df = pd.DataFrame(
        {"x": [5.0, 5.0, 5.0, 1.0]},
        index=pd.Index([2001, 2002, 2003, 2004], name="Year"),
    )
    out = cmpi_core._percentile_assign(df.copy(), "x", ascending=True)
    # Ties at ranks 2..4 average to rank 3: Pos = (3-1)/4 for all three.
    assert out["xPos"].tolist() == pytest.approx([0.5, 0.5, 0.5, 0.0])


def test_percentile_assign_rejects_nan() -> None:
    df = pd.DataFrame({"x": [1.0, None]}, index=pd.Index([2001, 2002], name="Year"))
    with pytest.raises(ValueError, match="NaN innovations"):
        cmpi_core._percentile_assign(df.copy(), "x", ascending=True)


def test_compute_innovations_scores_every_term_year_against_inherited_baseline() -> None:
    terms = [("A", 2001, 2002, "", "m1"), ("B", 2003, 2003, "", "m2")]

    def year_value_fn(year: int) -> pd.Series:
        return pd.Series({"Inflation": float(year)})

    innov = cmpi_core.compute_innovations(terms, year_value_fn)
    # Term A inherits 2000's level for both of its years; B inherits 2002's.
    assert innov.loc[2001, "Inflation"] == pytest.approx(1.0)
    assert innov.loc[2002, "Inflation"] == pytest.approx(2.0)
    assert innov.loc[2003, "Inflation"] == pytest.approx(1.0)
    assert innov["Term"].tolist() == ["A", "A", "B"]


def test_interpolate_fpi_ratio_gaps_is_linear_between_observed_endpoints() -> None:
    hist = pd.DataFrame(
        {"Result_Revenue": [0.10, None, None, None, 0.30],
         "Result_DebtServ": [-0.20, None, None, None, 0.40]},
        index=pd.Index([1860, 1861, 1862, 1863, 1864], name="Year"),
    )
    out = cmpi_core.interpolate_fpi_ratio_gaps(hist)
    assert out.loc[1861, "Result_Revenue"] == pytest.approx(0.15)
    assert out.loc[1862, "Result_Revenue"] == pytest.approx(0.20)
    assert out.loc[1863, "Result_Revenue"] == pytest.approx(0.25)
    assert out.loc[1861, "Result_DebtServ"] == pytest.approx(-0.05)
    assert out.loc[1863, "Result_DebtServ"] == pytest.approx(0.25)


def test_interpolate_fpi_ratio_gaps_requires_blank_source_cells() -> None:
    hist = pd.DataFrame(
        {"Result_Revenue": [0.10, 0.99, None, None, 0.30],
         "Result_DebtServ": [-0.20, None, None, None, 0.40]},
        index=pd.Index([1860, 1861, 1862, 1863, 1864], name="Year"),
    )
    with pytest.raises(ValueError, match="must be blank"):
        cmpi_core.interpolate_fpi_ratio_gaps(hist)


# --- Headline claims pinned to pipeline output ------------------------------


def _overall_table() -> pd.DataFrame:
    path = ROOT / "paper" / "generated" / "tbl_overall.md"
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells[0] in ("Administration", "") or set(cells[0]) <= {":", "-"}:
            continue
        rows.append(
            {
                "Administration": cells[0],
                "Rank": int(cells[1]),
                "Years": cells[2],
                "Overall": float(cells[-1]),
            }
        )
    if not rows:
        pytest.fail(f"No rows parsed from {path}")
    return pd.DataFrame(rows)


def test_full_pool_covers_41_administrations_once() -> None:
    overall = _overall_table()
    assert len(overall) == 41
    assert sorted(overall["Rank"]) == list(range(1, 42))


def test_headline_podium_membership_is_pinned() -> None:
    """Refactor guard: no silent reorder of Menem / Obligado / Milei.

    Table 11 establishes podium *membership* robustness, not order; this pin
    holds the membership fixed across refactors.
    """
    overall = _overall_table()
    podium = overall.nsmallest(3, "Rank")["Administration"].tolist()
    assert sorted(podium) == ["Menem", "Milei", "Obligado"]
    assert overall.iloc[0]["Administration"] == "Menem"


def test_alsina_constructed_baseline_last_place_is_pinned() -> None:
    overall = _overall_table()
    last = overall.nlargest(1, "Rank").iloc[0]
    assert last["Administration"] == "Alsina"
    assert last["Years"] == "1853–1853"
