#!/usr/bin/env python3
"""Audit scripts/ for post-2000 numeric constants that could hide baseline data in Python.

The fiscal/macro pipeline must not carry post-2000 baseline-affecting values as Python
constants when a raw/downloaded or provenance-rich file source can carry them instead. This
script scans every module under scripts/ for module-level year-keyed numeric tables (dicts
keyed by years 2000-2026, or lists of (year, value, ...) tuples) and classifies each:

    code_constant  — a hardcoded year->value table NOT on the allowlist. If it affects baseline
                     years >= 2000, the audit FAILS (exit 1).
    test_fixture   — allowlisted drift tripwires / cross-references never written to baseline.
    legal_fact     — allowlisted exact institutional constants (e.g. the 1:1 convertibility peg).

Exit code: 0 if no un-allowlisted code_constant affects baseline years >= 2000, else 1.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"

YEAR_LO, YEAR_HI = 2000, 2026

# name -> (classification, reason). Anything detected and listed here is NOT a failure.
ALLOWLIST: dict[str, tuple[str, str]] = {
    "AN_DEVENGADO_SNAPSHOT": (
        "test_fixture",
        "AN-devengado drift tripwire; printed cross-reference only, never written to baseline output",
    ),
    "AN_DRIFT_TOLERANCE": (
        "test_fixture",
        "scalar tolerance for the AN-devengado upstream-revision tripwire",
    ),
    "CONVERTIBILITY": (
        "legal_fact",
        "Ley de Convertibilidad 23928 pegged ARS 1:1 to USD by law through Jan 2002; exact, not an estimate",
    ),
    "EXPECTED_VALUES_USD_M": (
        "test_fixture",
        "drift tripwire for official BCRA parser output; validates but never supplies output values",
    ),
}


def _is_number(node: ast.AST) -> bool:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return True
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        return _is_number(node.operand)
    return False


def _number_value(node: ast.AST) -> float | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        inner = _number_value(node.operand)
        if inner is None:
            return None
        return -inner if isinstance(node.op, ast.USub) else inner
    return None


def _looks_like_year(value: float | None) -> bool:
    return value is not None and value.is_integer() and 1900 <= value <= 2100


def _year_keys_from_dict(node: ast.Dict) -> list[int]:
    """Years 2000-2026 used as dict keys whose values are non-year numeric payloads."""
    years: list[int] = []
    for key, val in zip(node.keys, node.values):
        kv = _number_value(key) if key is not None else None
        if kv is None or not kv.is_integer():
            continue
        if not (YEAR_LO <= kv <= YEAR_HI):
            continue
        # value must be a numeric payload (scalar, or tuple/list of numbers) that is not itself a year
        payload_numeric = False
        if _is_number(val) and not _looks_like_year(_number_value(val)):
            payload_numeric = True
        elif isinstance(val, (ast.Tuple, ast.List)) and any(_is_number(e) for e in val.elts):
            payload_numeric = True
        if payload_numeric:
            years.append(int(kv))
    return years


def _year_keys_from_seq(node: ast.AST) -> list[int]:
    """Years 2000-2026 as the leading element of (year, value, ...) tuples in a list/tuple."""
    if not isinstance(node, (ast.List, ast.Tuple)):
        return []
    years: list[int] = []
    for elt in node.elts:
        if not isinstance(elt, ast.Tuple) or len(elt.elts) < 2:
            continue
        yv = _number_value(elt.elts[0])
        if yv is None or not yv.is_integer() or not (YEAR_LO <= yv <= YEAR_HI):
            continue
        if any(_is_number(e) for e in elt.elts[1:]):
            years.append(int(yv))
    return years


def scan_file(path: Path) -> list[dict[str, object]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    findings: list[dict[str, object]] = []
    for node in tree.body:  # module-level assignments only
        if not isinstance(node, ast.Assign):
            continue
        names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if not names:
            continue
        if isinstance(node.value, ast.Dict):
            years = _year_keys_from_dict(node.value)
        else:
            years = _year_keys_from_seq(node.value)
        if not years:
            continue
        for name in names:
            classification, reason = ALLOWLIST.get(name, ("code_constant", ""))
            affects_baseline = classification == "code_constant" and max(years) >= YEAR_LO
            findings.append(
                {
                    "file": str(path.relative_to(ROOT)),
                    "variable_family": name,
                    "year_lo": min(years),
                    "year_hi": max(years),
                    "classification": classification,
                    "affects_baseline": affects_baseline,
                    "reason": reason,
                }
            )
    return findings


def main() -> int:
    all_findings: list[dict[str, object]] = []
    for path in sorted(SCRIPTS_DIR.glob("*.py")):
        if path.name == Path(__file__).name:
            continue
        all_findings.extend(scan_file(path))

    header = f"{'file':<48} {'years':<11} {'variable_family':<28} {'classification':<14} affects_baseline"
    print(header)
    print("-" * len(header))
    for f in all_findings:
        years = f"{f['year_lo']}-{f['year_hi']}" if f["year_lo"] != f["year_hi"] else f"{f['year_lo']}"
        print(
            f"{f['file']:<48} {years:<11} {f['variable_family']:<28} "
            f"{f['classification']:<14} {f['affects_baseline']}"
        )
    if not all_findings:
        print("(no post-2000 year-keyed numeric constants found)")

    violations = [f for f in all_findings if f["affects_baseline"]]
    if violations:
        print("\nFAIL: the following code_constant(s) affect baseline years >= 2000 and must be "
              "moved to a raw/downloaded or provenance-rich file source:", file=sys.stderr)
        for f in violations:
            print(f"  {f['file']}: {f['variable_family']} ({f['year_lo']}-{f['year_hi']})", file=sys.stderr)
        return 1

    print("\nPASS: no un-allowlisted post-2000 code_constant affects baseline.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
