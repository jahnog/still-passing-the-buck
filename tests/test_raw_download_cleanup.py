"""Retention of rotated raw downloads: keep the last two copies per dest."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_io import (
    atomic_write_bytes,
    cleanup_rotated_raw,
    parse_rotated_filename,
    prune_rotated_versions,
    rotate_existing,
    rotation_sidecar,
    write_meta_sidecar,
)


def test_parse_rotated_filename_keeps_date_and_year_tokens():
    assert parse_rotated_filename("api_cotizaciones-blue_2012-01_2025-12.json") == (
        "api_cotizaciones-blue_2012-01_2025-12.json",
        0,
    )
    assert parse_rotated_filename("api_cotizaciones-blue_2012-01_2025-12_4.json") == (
        "api_cotizaciones-blue_2012-01_2025-12.json",
        4,
    )
    assert parse_rotated_filename("imig-anual_2017.xlsx") == ("imig-anual_2017.xlsx", 0)
    assert parse_rotated_filename("imig-anual_2018.xlsx") == ("imig-anual_2018.xlsx", 0)
    assert parse_rotated_filename("imig-anual_1.xlsx") == ("imig-anual.xlsx", 1)
    assert parse_rotated_filename("spn-base-caja_valores-anuales_1993_2006.csv") == (
        "spn-base-caja_valores-anuales_1993_2006.csv",
        0,
    )
    assert parse_rotated_filename("spn-base-caja_valores-anuales_2015_2025_raw_3.csv") == (
        "spn-base-caja_valores-anuales_2015_2025_raw.csv",
        3,
    )
    assert parse_rotated_filename("deuda_deuda-publica_2019-01_2019-12.xlsx") == (
        "deuda_deuda-publica_2019-01_2019-12.xlsx",
        0,
    )


def test_rotate_existing_preserves_year_token_in_dest(tmp_path: Path):
    dest = tmp_path / "imig-anual_2017.xlsx"
    dest.write_bytes(b"2017-live")
    rotate_existing(dest)
    backup = tmp_path / "imig-anual_2017_1.xlsx"
    assert backup.read_bytes() == b"2017-live"
    assert not dest.exists()
    assert not (tmp_path / "imig-anual_1.xlsx").exists()


def test_rotate_existing_increments_and_moves_sidecar(tmp_path: Path):
    dest = tmp_path / "publicaciones_com3500_1960-01_2025-12.xls"
    dest.write_bytes(b"first")
    write_meta_sidecar(dest, script="test.py", sources=["https://example.test/a"])
    rotate_existing(dest)

    first = tmp_path / "publicaciones_com3500_1960-01_2025-12_1.xls"
    assert not dest.exists()
    assert first.read_bytes() == b"first"
    assert rotation_sidecar(first).is_file()
    assert not rotation_sidecar(dest).exists()

    dest.write_bytes(b"second")
    write_meta_sidecar(dest, script="test.py", sources=["https://example.test/b"])
    rotate_existing(dest)

    second = tmp_path / "publicaciones_com3500_1960-01_2025-12_2.xls"
    assert first.read_bytes() == b"first"
    assert second.read_bytes() == b"second"
    assert rotation_sidecar(second).is_file()
    assert not dest.exists()


def test_prune_keeps_live_and_previous_copy(tmp_path: Path):
    dest = tmp_path / "wdi_wdi-csv_1960-01_2025-12.zip"
    dest.write_bytes(b"live")
    for generation, payload in ((1, b"oldest"), (2, b"old"), (3, b"prev")):
        member = tmp_path / f"wdi_wdi-csv_1960-01_2025-12_{generation}.zip"
        member.write_bytes(payload)
        rotation_sidecar(member).write_text("{}", encoding="utf-8")

    removed = prune_rotated_versions(dest, keep=2)
    assert dest.read_bytes() == b"live"
    assert (tmp_path / "wdi_wdi-csv_1960-01_2025-12_3.zip").read_bytes() == b"prev"
    assert {path.name for path in removed} == {
        "wdi_wdi-csv_1960-01_2025-12_1.zip",
        "wdi_wdi-csv_1960-01_2025-12_1.zip.meta.json",
        "wdi_wdi-csv_1960-01_2025-12_2.zip",
        "wdi_wdi-csv_1960-01_2025-12_2.zip.meta.json",
    }
    remaining = {path.name for path in tmp_path.iterdir()}
    assert remaining == {
        "wdi_wdi-csv_1960-01_2025-12.zip",
        "wdi_wdi-csv_1960-01_2025-12_3.zip",
        "wdi_wdi-csv_1960-01_2025-12_3.zip.meta.json",
    }


def test_cleanup_does_not_merge_hacienda_year_files(tmp_path: Path):
    hacienda = tmp_path / "hacienda"
    hacienda.mkdir()
    current_2017 = hacienda / "imig-anual_2017.xlsx"
    current_2018 = hacienda / "imig-anual_2018.xlsx"
    current_2017.write_bytes(b"2017")
    current_2018.write_bytes(b"2018")
    leftover = hacienda / "imig-anual_11.xlsx"
    leftover.write_bytes(b"stray")
    (hacienda / "imig-anual_10.xlsx").write_bytes(b"stray-old")
    (hacienda / "imig-anual_9.xlsx").write_bytes(b"stray-older")
    (hacienda / "spn-base-caja_valores-anuales_1993_2006.csv").write_bytes(b"live-1993")
    (hacienda / "spn-base-caja_valores-anuales_1993_1.csv").write_bytes(b"buggy-1")
    (hacienda / "spn-base-caja_valores-anuales_1993_2.csv").write_bytes(b"buggy-2")
    (hacienda / "spn-base-caja_valores-anuales_1993_3.csv").write_bytes(b"buggy-3")

    removed = cleanup_rotated_raw(tmp_path, keep=2)
    assert current_2017.exists()
    assert current_2018.exists()
    assert leftover.exists()
    assert (hacienda / "imig-anual_10.xlsx").exists()
    assert not (hacienda / "imig-anual_9.xlsx").exists()
    assert (hacienda / "spn-base-caja_valores-anuales_1993_2006.csv").exists()
    assert (hacienda / "spn-base-caja_valores-anuales_1993_3.csv").exists()
    assert (hacienda / "spn-base-caja_valores-anuales_1993_2.csv").exists()
    assert not (hacienda / "spn-base-caja_valores-anuales_1993_1.csv").exists()
    assert {path.name for path in removed} == {
        "imig-anual_9.xlsx",
        "spn-base-caja_valores-anuales_1993_1.csv",
    }


def test_atomic_write_prunes_to_two_copies(tmp_path: Path):
    dest = tmp_path / "api_ny-gdp-mktp-cd_1960-01_2025-12.json"
    for payload in (b"v1", b"v2", b"v3", b"v4"):
        atomic_write_bytes(payload, dest)

    names = sorted(path.name for path in tmp_path.iterdir() if not path.name.startswith("."))
    assert names == [
        "api_ny-gdp-mktp-cd_1960-01_2025-12.json",
        "api_ny-gdp-mktp-cd_1960-01_2025-12_3.json",
    ]
    assert dest.read_bytes() == b"v4"
    assert (tmp_path / "api_ny-gdp-mktp-cd_1960-01_2025-12_3.json").read_bytes() == b"v3"


def test_cleanup_dry_run_leaves_files(tmp_path: Path):
    dest = tmp_path / "file.json"
    dest.write_bytes(b"live")
    extra = tmp_path / "file_1.json"
    extra.write_bytes(b"old")
    previous = tmp_path / "file_2.json"
    previous.write_bytes(b"prev")

    removed = cleanup_rotated_raw(tmp_path, keep=2, dry_run=True)
    assert extra.exists()
    assert previous.exists()
    assert dest.exists()
    assert [path.name for path in removed] == ["file_1.json"]
