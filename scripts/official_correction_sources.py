"""Pinned official artifacts used by the F-05 correction generators."""

from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from pathlib import Path

from scripts.data_io import RAW_ROOT, atomic_download, write_meta_sidecar


@dataclass(frozen=True)
class OfficialSource:
    source_id: str
    provider: str
    publisher: str
    title: str
    reference_date: str
    url: str
    artifact: Path
    min_size: int = 1_000


def _raw(provider: str, name: str) -> Path:
    return RAW_ROOT / provider / name


SOURCES: tuple[OfficialSource, ...] = (
    *(
        OfficialSource(
            source_id=f"bcra-congress-report-{year}",
            provider="bcra",
            publisher="Banco Central de la República Argentina",
            title=f"Informe Anual al Honorable Congreso de la Nación Argentina — Año {year}",
            reference_date=f"{year}-12-31",
            url=(
                "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/"
                f"inf{year}.pdf"
            ),
            artifact=_raw(
                "bcra",
                f"publicaciones_informe-congreso_{year}-01_{year}-12.pdf",
            ),
            min_size=100_000,
        )
        for year in range(2009, 2016)
    ),
    OfficialSource(
        source_id="afip-revenue-report-2016",
        provider="afip",
        publisher="Administración Federal de Ingresos Públicos",
        title="Informe de Recaudación — cuarto trimestre de 2016",
        reference_date="2016-12-31",
        url=(
            "https://contenidos.afip.gob.ar/institucional/estudios/archivos/"
            "informe.4.trimestre.2016.pdf"
        ),
        artifact=_raw("afip", "estudios_informe-recaudacion_2016-01_2016-12.pdf"),
        min_size=100_000,
    ),
    OfficialSource(
        source_id="afip-revenue-report-2017",
        provider="afip",
        publisher="Administración Federal de Ingresos Públicos",
        title="Informe de Recaudación — cuarto trimestre de 2017",
        reference_date="2017-12-31",
        url=(
            "https://contenidos.afip.gob.ar/institucional/estudios/archivos/"
            "informe.4.trimestre.2017.pdf"
        ),
        artifact=_raw("afip", "estudios_informe-recaudacion_2017-01_2017-12.pdf"),
        min_size=100_000,
    ),
    OfficialSource(
        source_id="arca-revenue-report-2024",
        provider="afip",
        publisher="Agencia de Recaudación y Control Aduanero",
        title="Recaudación Tributaria — Año 2024",
        reference_date="2024-12-31",
        url="https://www.afip.gob.ar/institucional/documentos/ARCA-Recaudacion-ANUAL2024.pdf",
        artifact=_raw("afip", "recaudacion_informe-anual_2024-01_2024-12.pdf"),
        min_size=50_000,
    ),
    OfficialSource(
        source_id="arca-revenue-report-2024-11",
        provider="afip",
        publisher="Agencia de Recaudación y Control Aduanero",
        title="Recaudación Tributaria — Noviembre 2024",
        reference_date="2024-11-30",
        url=(
            "https://www.arca.gob.ar/institucional/documentos/"
            "recaudacion-tributaria-112024.pdf"
        ),
        artifact=_raw("afip", "recaudacion_informe-mensual_2024-11_2024-11.pdf"),
        min_size=50_000,
    ),
    OfficialSource(
        source_id="opc-budget-report-2022",
        provider="opc",
        publisher="Oficina de Presupuesto del Congreso",
        title="Descripción general del Proyecto de Ley de Presupuesto 2022",
        reference_date="2021-09-30",
        url="https://opc.gob.ar/download/19142/",
        artifact=_raw("opc", "presupuesto_descripcion-general-2022_2021-09_2021-09.pdf"),
        min_size=50_000,
    ),
    OfficialSource(
        source_id="opc-debt-operations-2024-12",
        provider="opc",
        publisher="Oficina de Presupuesto del Congreso",
        title="Operaciones de Deuda Pública — Diciembre 2024",
        reference_date="2024-12-31",
        url="https://opc.gob.ar/download/40009/?tmstv=1738608772",
        artifact=_raw("opc", "deuda_operaciones-publicas_2024-12_2024-12.pdf"),
        min_size=20_000,
    ),
    *(
        OfficialSource(
            source_id=f"opc-debt-operations-2025-{month:02d}",
            provider="opc",
            publisher="Oficina de Presupuesto del Congreso",
            title=f"Operaciones de Deuda Pública — 2025-{month:02d}",
            reference_date=f"2025-{month:02d}-{monthrange(2025, month)[1]:02d}",
            url=f"https://opc.gob.ar/download/{download_id}/?tmstv={timestamp}",
            artifact=_raw(
                "opc",
                f"deuda_operaciones-publicas_2025-{month:02d}_2025-{month:02d}.pdf",
            ),
            min_size=20_000,
        )
        for month, download_id, timestamp in (
            (1, 40226, 1741629314),
            (2, 40625, 1743189177),
            (3, 42316, 1745867086),
            (4, 43578, 1748617317),
            (5, 44169, 1751041290),
            (6, 44917, 1753302302),
            (7, 45876, 1758233776),
            (8, 45998, 1758742017),
            (9, 47165, 1761759516),
            (10, 47714, 1764702780),
            (11, 48062, 1767022280),
        )
    ),
    OfficialSource(
        source_id="opc-debt-operations-2025-12",
        provider="opc",
        publisher="Oficina de Presupuesto del Congreso",
        title="Operaciones de Deuda Pública — Diciembre 2025",
        reference_date="2025-12-31",
        url="https://opc.gob.ar/download/48488/?tmstv=1769707199",
        artifact=_raw("opc", "deuda_operaciones-publicas_2025-12_2025-12.pdf"),
        min_size=20_000,
    ),
    OfficialSource(
        source_id="ipec-santa-fe-cpi-2005-2013",
        provider="santafe",
        publisher="Instituto Provincial de Estadística y Censos de Santa Fe",
        title="Índice de Precios al Consumidor de la Provincia de Santa Fe, 2005–2013",
        reference_date="2013-12-31",
        url=(
            "https://www.santafe.gov.ar/index.php/web/content/download/109537/540514/file/"
            "cIndice%20Pcia%202005-2013.xls"
        ),
        artifact=_raw("santafe", "ipec_indice-precios-consumidor_2005-01_2013-12.xls"),
        min_size=20_000,
    ),
    OfficialSource(
        source_id="ipec-santa-fe-cpi-2017-release",
        provider="santafe",
        publisher="Instituto Provincial de Estadística y Censos de Santa Fe",
        title="Índice de Precios al Consumidor de Santa Fe — Diciembre 2017",
        reference_date="2017-12-31",
        url=(
            "https://www.santafe.gov.ar/index.php/web/content/download/243468/1282154/"
            "version/2/file/1217.pdf"
        ),
        artifact=_raw("santafe", "ipec_ipc-santa-fe_2017-12_2017-12.pdf"),
        min_size=100_000,
    ),
    OfficialSource(
        source_id="dgeyc-caba-cpi-2012-2015",
        provider="caba",
        publisher="Dirección General de Estadística y Censos de la Ciudad de Buenos Aires",
        title="IPCBA — evolución del nivel general, bienes y servicios",
        reference_date="2015-12-31",
        url=(
            "https://www.estadisticaciudad.gob.ar/eyc/wp-content/uploads/2022/02/"
            "Evol_gral_bs_svcios.xlsx"
        ),
        artifact=_raw("caba", "dgeyc_ipcba-nivel-general_2012-07_2015-12.xlsx"),
        min_size=10_000,
    ),
    OfficialSource(
        source_id="dpec-san-luis-cpi-2013-2015",
        provider="sanluis",
        publisher="Dirección Provincial de Estadística y Censos de San Luis",
        title="IPC San Luis — nivel general, bienes y servicios",
        reference_date="2016-01-31",
        url=(
            "https://estadistica.sanluis.gov.ar/documents/Economia/Precios/"
            "IPC%20San%20Luis/lbycc1cu.pdf"
        ),
        artifact=_raw("sanluis", "dpec_ipc-san-luis_2013-01_2016-01.pdf"),
        min_size=100_000,
    ),
)


def sources_for(provider: str) -> list[OfficialSource]:
    return [source for source in SOURCES if source.provider == provider]


def download_provider(provider: str, *, script: str) -> int:
    sources = sources_for(provider)
    if not sources:
        raise ValueError(f"Unknown official-source provider: {provider}")
    for source in sources:
        source.artifact.parent.mkdir(parents=True, exist_ok=True)
        if source.artifact.exists():
            if source.artifact.stat().st_size < source.min_size:
                raise RuntimeError(f"Existing pinned artifact is too small: {source.artifact}")
            print(f"Retained {source.artifact.relative_to(RAW_ROOT.parent.parent)}")
            continue
        atomic_download(source.url, source.artifact, min_size=source.min_size)
        write_meta_sidecar(
            source.artifact,
            script=script,
            sources=[source.url],
            notes=(
                f"{source.title}; reference date {source.reference_date}. "
                "Pinned official artifact for row-level correction provenance."
            ),
        )
        print(f"Wrote {source.artifact.relative_to(RAW_ROOT.parent.parent)}")
    return 0
