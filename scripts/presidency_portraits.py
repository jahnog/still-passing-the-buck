"""Local portrait assets for president and economy-minister table cells."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PORTRAITS_DIR = ROOT / "assets" / "portraits"
MANIFEST_PATH = PORTRAITS_DIR / "manifest.json"

MAX_PORTRAIT_PX = 100

# Source URLs mirrored from Historical_CMPI_Extension.ipynb presidency_terms (2025-06).
PORTRAIT_SOURCE_URLS: tuple[str, ...] = (
    "https://upload.wikimedia.org/wikipedia/commons/a/a1/Valentin_alsina_retrato.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/3/36/Pastor_Obligado.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/1/1c/Bartolom%C3%A9_Mitre_01.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/6/60/Dr._Dalmacio_V%C3%A9lez_Sarsfield.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/9/9d/Sarmiento.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/c/cc/Nicol%C3%A1s_Avellaneda_-_1910.JPG",
    "https://upload.wikimedia.org/wikipedia/commons/f/f7/RetratoROcaMuseo.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/0/0e/Juarez_celman_president.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/a/ab/Retrato_de_Carlos_Pellegrini.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/8/8f/Luis_Saenz_Pena.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/b/b6/Manuel_Quintana_presidente.png",
    "https://upload.wikimedia.org/wikipedia/commons/6/6c/Roque_Saenz_Pena.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/3/30/Hipolito_Yrigoyen_-_NAC.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/7/7f/Marcelo_T._de_Alvear%2C_ca._1915.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/0/08/Jose_Uriburu.png",
    "https://upload.wikimedia.org/wikipedia/commons/1/1a/Presidente_Agust%C3%ADn_Pedro_Justo.png",
    "https://upload.wikimedia.org/wikipedia/commons/3/36/Roberto_Ortiz_President.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/1/1d/Pedro-p-ramirez.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/b/bc/Juan_Domingo_Per%C3%B3n_1973.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/e/e4/Pedro_Eugenio_Aramburu.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/e/ee/Adalbert_Krieger_Vasena.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/1/1d/Arturo_Frondizi.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/e/e4/%C3%81lvaro_Alsogaray_d%C3%A9cada_de_1960.png",
    "https://upload.wikimedia.org/wikipedia/commons/9/9c/Jos%C3%A9_Mar%C3%ADa_Guido_3_%28cropped%29_2.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/2/2b/Illia_banda_presidencial.jpg",
    "https://cdi.mecon.gob.ar/img/pugliese.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/0/00/Juan_Carlos_Ongan%C3%ADa.JPG",
    "https://cdi.mecon.gob.ar/img/krieguer.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/7/7e/Alejandro_Agust%C3%ADn_Lanusse.jpg",
    "https://cdi.mecon.gob.ar/img/Wehbe.jpg",
    "https://cdi.mecon.gob.ar/img/rodrigo.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/e/e5/Retrato_Oficial_Jorge_Rafael_Videla_1976.jpg",
    "https://cdi.mecon.gob.ar/img/martinez.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/e/e4/Ra%C3%BAl_Alfons%C3%ADn_con_banda_presidencial.jpg",
    "https://cdi.mecon.gob.ar/img/sorrou.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/1/14/Menem_con_banda_presidencial.jpg",
    "https://cdi.mecon.gob.ar/img/cavallo.jpg",
    "https://cdi.mecon.gob.ar/img/rfernadez.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/b/b5/Fernando_de_la_R%C3%BAa_con_bast%C3%B3n_y_banda_de_presidente.jpg",
    "https://cdi.mecon.gob.ar/img/machinea.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/9/91/Eduardo_duhalde_presidente.jpg",
    "https://cdi.mecon.gob.ar/img/lavagna.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/d/db/NestorKirchner.jpeg",
    "https://cdi.mecon.gob.ar/img/micelli.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/9/92/Cristina_Fernandez_de_Kirchner_-_Foto_Oficial_2.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/4/4b/Amado_Boudou.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/1/1c/Ak_cong_006.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/4/44/Retrato_oficial_del_Presidente_Mauricio_Macri.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/3/35/NicolasDujovne_%28cropped%29.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/2/27/Mensaje_de_fin_de_a%C3%B1o_del_Presidente_Alberto_Fern%C3%A1ndez_%28cropped%29.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/5/55/Ministro_Mart%C3%ADn_M._Guzm%C3%A1n_%28cropped%29.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/f/f5/Sergio_Massa_-_Presentaci%C3%B3n_nueva_l%C3%ADnea_de_financiamiento_para_la_producci%C3%B3n_de_contenidos_audiovisuales_%28cropped2%29.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/7/76/Javier_Milei_in_pull-aside_meeting_at_the_United_Nations_Headquarters_%283x4_cropped%29.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/0/08/Caputocepo_%28cropped%29.jpg",
)


def portrait_filename(url: str) -> str:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return f"{digest}.jpg"


def portrait_relative_path(url: str) -> str:
    return f"assets/portraits/{portrait_filename(url)}"


def _urls_from_minister_field(raw: str) -> list[str]:
    parts = [p.strip() for p in raw.split("|") if p.strip()]
    urls: list[str] = []
    i = 0
    while i < len(parts):
        part = parts[i]
        if part.startswith("http"):
            urls.append(part)
            i += 1
        else:
            if i + 1 < len(parts) and parts[i + 1].startswith("http"):
                urls.append(parts[i + 1])
                i += 2
            else:
                i += 1
    return urls


def collect_portrait_urls(presidency_terms: list[tuple[Any, ...]]) -> list[str]:
    """Return deduplicated portrait URLs from presidency_terms tuples."""
    seen: set[str] = set()
    ordered: list[str] = []
    for _name, _fy, _ly, president_url, minister_field in presidency_terms:
        for url in [str(president_url).strip(), *_urls_from_minister_field(str(minister_field))]:
            if url.startswith("http") and url not in seen:
                seen.add(url)
                ordered.append(url)
    return ordered


def load_manifest() -> dict[str, dict[str, Any]]:
    if not MANIFEST_PATH.is_file():
        return {}
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def save_manifest(manifest: dict[str, dict[str, Any]]) -> None:
    PORTRAITS_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def local_path_for_url(url: str, manifest: dict[str, dict[str, Any]] | None = None) -> str:
    """Map a source URL to a repo-relative local portrait path."""
    if manifest is None:
        manifest = load_manifest()
    entry = manifest.get(url)
    if entry and entry.get("path"):
        return str(entry["path"])
    return portrait_relative_path(url)


def _localize_minister_field(raw: str, manifest: dict[str, dict[str, Any]]) -> str:
    if not str(raw).strip():
        return str(raw)
    parts = [p.strip() for p in str(raw).split("|") if p.strip()]
    out: list[str] = []
    i = 0
    while i < len(parts):
        part = parts[i]
        if part.startswith("http"):
            out.append(local_path_for_url(part, manifest))
            i += 1
        else:
            name = part
            if i + 1 < len(parts) and parts[i + 1].startswith("http"):
                out.append(name)
                out.append(local_path_for_url(parts[i + 1], manifest))
                i += 2
            else:
                out.append(name)
                i += 1
    return "|".join(out)


def localize_presidency_terms(
    presidency_terms: list[tuple[Any, ...]],
) -> list[tuple[Any, ...]]:
    """Swap remote portrait URLs for local assets/portraits paths."""
    manifest = load_manifest()
    localized: list[tuple[Any, ...]] = []
    for name, fy, ly, president_url, minister_field in presidency_terms:
        pres = str(president_url).strip()
        if pres.startswith("http"):
            pres = local_path_for_url(pres, manifest)
        localized.append(
            (name, fy, ly, pres, _localize_minister_field(str(minister_field), manifest))
        )
    return localized
