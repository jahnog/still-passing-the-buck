#!/usr/bin/env python3

from __future__ import annotations

import argparse
import base64
import hashlib
import mimetypes
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


PRINT_CSS = """
@page {
    size: %(page_size)s;
    margin: 18mm 16mm 18mm 16mm;
}

html {
    print-color-adjust: exact;
    -webkit-print-color-adjust: exact;
}

body.paper-export {
    background: #ffffff;
    color: #1b1b1b;
    font-family: "Libertinus Serif", "Source Serif 4", "Noto Serif", "Charter", Georgia, serif;
    font-size: 11pt;
    line-height: 1.58;
    margin: 0;
}

.paper-export .jp-Notebook,
.paper-export #notebook-container,
.paper-export main {
    margin: 0 auto !important;
    max-width: none !important;
    padding: 0 !important;
}

.paper-export .jp-Cell,
.paper-export .cell {
    margin: 0 0 0.95rem 0 !important;
    page-break-inside: avoid;
}

.paper-export .jp-RenderedHTMLCommon,
.paper-export .rendered_html {
    color: inherit;
    font-family: inherit;
    font-size: inherit;
    line-height: inherit;
    padding: 0 !important;
}

.paper-export h1,
.paper-export h2,
.paper-export h3,
.paper-export h4 {
    color: #111111;
    font-family: "Libertinus Sans", "Source Sans 3", "Noto Sans", "Avenir Next", Arial, sans-serif;
    font-weight: 650;
    line-height: 1.18;
    page-break-after: avoid;
}

.paper-export h1 {
    font-size: 24pt;
    letter-spacing: -0.02em;
    margin: 0 0 0.2in 0;
}

.paper-export h1 + h3 {
    color: #4b4b4b;
    font-size: 13.5pt;
    font-weight: 500;
    margin: 0 0 0.22in 0;
}

.paper-export h2 {
    border-bottom: 1px solid #d7d7d7;
    font-size: 16pt;
    margin: 1.1rem 0 0.55rem 0;
    padding-bottom: 0.15rem;
}

.paper-export h3 {
    font-size: 12.5pt;
    margin: 0.9rem 0 0.35rem 0;
}

.paper-export p,
.paper-export li {
    hyphens: auto;
    margin: 0 0 0.55rem 0;
    orphans: 3;
    text-align: justify;
    widows: 3;
}

.paper-export ul,
.paper-export ol {
    margin: 0 0 0.8rem 1.25rem;
    padding: 0;
}

.paper-export strong {
    color: #111111;
}

.paper-export a {
    color: #0e3a67;
    text-decoration: none;
}

.paper-export hr {
    border: 0;
    border-top: 1px solid #dddddd;
    margin: 1rem 0;
}

.paper-export img,
.paper-export svg,
.paper-export canvas {
    display: block;
    height: auto !important;
    margin: 0.5rem auto 0.7rem auto;
    max-width: 100%% !important;
    page-break-inside: avoid;
}

.paper-export table,
.paper-export .dataframe {
    border-collapse: collapse;
    font-size: 8.8pt;
    margin: 0.55rem 0 0.85rem 0;
    page-break-inside: auto;
    table-layout: fixed;
    width: 100%%;
}

.paper-export thead {
    display: table-header-group;
}

.paper-export tr {
    page-break-inside: avoid;
}

.paper-export th,
.paper-export td {
    border: 1px solid #cfcfcf;
    overflow-wrap: anywhere;
    padding: 0.28rem 0.4rem;
    vertical-align: top;
}

.paper-export th {
    background: #f3f4f6;
    font-family: "Libertinus Sans", "Source Sans 3", "Noto Sans", Arial, sans-serif;
    font-weight: 650;
}

.paper-export th:nth-last-child(-n+2),
.paper-export td:nth-last-child(-n+2) {
    min-width: 72px;
    text-align: center;
    width: 10%%;
}

.paper-export td:nth-last-child(-n+2) > div {
    align-items: center !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 4px !important;
    justify-content: flex-start !important;
    margin: 0 auto !important;
    max-width: 72px !important;
    min-width: 0 !important;
    width: 100%% !important;
}

.paper-export td:nth-last-child(-n+2) > div > div {
    align-items: center !important;
    display: flex !important;
    height: 72px !important;
    justify-content: center !important;
    margin: 0 auto !important;
    max-width: 72px !important;
    overflow: hidden !important;
    width: 72px !important;
}

.paper-export td:nth-last-child(-n+2) img {
    height: 100%% !important;
    margin: 0 auto !important;
    max-height: 72px !important;
    max-width: 72px !important;
    object-fit: contain !important;
    width: 100%% !important;
}

.paper-export pre,
.paper-export code,
.paper-export kbd,
.paper-export samp {
    font-family: "Iosevka Term", "JetBrains Mono", "Fira Code", "Source Code Pro", monospace;
}

.paper-export .jp-OutputArea-output pre,
.paper-export .output_text pre {
    background: #f7f7f7;
    border: 1px solid #e1e1e1;
    border-radius: 4px;
    font-size: 8.5pt;
    padding: 0.55rem 0.65rem;
    white-space: pre-wrap;
}

.paper-export .jp-RenderedHTMLCommon blockquote,
.paper-export blockquote {
    border-left: 3px solid #cdd5df;
    color: #333333;
    margin: 0.75rem 0;
    padding: 0.1rem 0 0.1rem 0.85rem;
}

.paper-export .jp-OutputArea,
.paper-export .output_wrapper,
.paper-export .output {
    overflow: visible !important;
}
"""


DEFAULT_BROWSERS = (
    "chromium",
    "chromium-browser",
    "google-chrome",
    "google-chrome-stable",
    "microsoft-edge",
)

DEFAULT_IMAGE_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
)
DEFAULT_IMAGE_TIMEOUT = 30
DEFAULT_IMAGE_RETRIES = 6
DEFAULT_HOST_DELAY_SECONDS = 2.0
WIKIMEDIA_HOST_SUFFIX = "wikimedia.org"
WIKIMEDIA_DELAY_SECONDS = 8.0


DEFAULT_NOTEBOOKS = (
    "Historical_CMPI_Extension.ipynb",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Render one or more notebooks as print-optimized PDF papers. "
            "With no notebook argument, renders the unified paper "
            "(Historical_CMPI_Extension.ipynb), the repository's only notebook."
        )
    )
    parser.add_argument(
        "notebooks",
        nargs="*",
        help="Notebook(s) to render. Defaults to the current unified paper.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help=(
            "Destination PDF path (single-notebook mode only). "
            "Defaults to <notebook>.paper.pdf. Ignored when rendering several notebooks."
        ),
    )
    parser.add_argument(
        "--output-dir",
        help="Directory for the generated PDFs in batch mode. Defaults to each notebook's directory.",
    )
    parser.add_argument(
        "--html-output",
        help="Optional path to keep the intermediate print HTML.",
    )
    parser.add_argument(
        "--browser",
        help="Browser binary to use for PDF printing. Defaults to an auto-detected Chromium/Chrome.",
    )
    parser.add_argument(
        "--kernel-name",
        help="Notebook kernel name. Defaults to the notebook metadata.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=900,
        help="Notebook execution timeout in seconds.",
    )
    parser.add_argument(
        "--virtual-time-budget-ms",
        type=int,
        default=20000,
        help="Extra browser render time budget before printing to PDF.",
    )
    parser.add_argument(
        "--page-size",
        choices=("A4", "Letter"),
        default="A4",
        help="Printed paper size.",
    )
    parser.add_argument(
        "--skip-execute",
        action="store_true",
        help="Render the notebook as-is without re-executing it.",
    )
    parser.add_argument(
        "--allow-errors",
        action="store_true",
        help="Keep going if notebook execution raises a cell error.",
    )
    return parser.parse_args()


def load_notebook_tools():
    try:
        import nbformat
        from nbconvert import HTMLExporter
        from nbconvert.preprocessors import ExecutePreprocessor
    except ImportError as exc:
        raise RuntimeError(
            "Missing notebook export dependencies. Install them with: pip install nbconvert nbformat"
        ) from exc
    return nbformat, HTMLExporter, ExecutePreprocessor


def resolve_browser(browser: str | None) -> str:
    candidates = (browser,) if browser else DEFAULT_BROWSERS
    for candidate in candidates:
        if not candidate:
            continue
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
        if Path(candidate).exists():
            return str(Path(candidate).resolve())
    raise RuntimeError(
        "No Chromium-compatible browser found. Install chromium or pass --browser /path/to/chrome."
    )


def inject_print_styles(html: str, page_size: str) -> str:
    style_block = "<style>\n%s\n</style>\n" % (PRINT_CSS % {"page_size": page_size})
    if "</head>" not in html:
        raise RuntimeError("Exported HTML did not contain a </head> tag.")
    html = html.replace("</head>", style_block + "</head>", 1)

    body_with_class = re.sub(
        r"<body([^>]*)class=\"([^\"]*)\"",
        lambda match: f'<body{match.group(1)}class="{match.group(2)} paper-export"',
        html,
        count=1,
    )
    if body_with_class != html:
        return body_with_class
    return html.replace("<body", '<body class="paper-export"', 1)


def guess_mime_type(url: str, response) -> str:
    content_type = response.headers.get_content_type()
    if content_type and content_type != "application/octet-stream":
        return content_type
    guessed, _encoding = mimetypes.guess_type(url)
    return guessed or "image/jpeg"


def build_data_uri(url: str, timeout: int) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": DEFAULT_IMAGE_USER_AGENT,
            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        mime_type = guess_mime_type(url, response)
        payload = base64.b64encode(response.read()).decode("ascii")
    return f"data:{mime_type};base64,{payload}"


def cache_path_for_url(cache_dir: Path, url: str) -> Path:
    parsed = urllib.parse.urlparse(url)
    suffix = Path(parsed.path).suffix or ".txt"
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
    return cache_dir / f"{digest}{suffix}.b64"


def wait_for_host(host: str, host_deadlines: dict[str, float], delay_seconds: float) -> None:
    now = time.monotonic()
    deadline = host_deadlines.get(host, now)
    if deadline > now:
        time.sleep(deadline - now)
    host_deadlines[host] = time.monotonic() + delay_seconds


def host_delay_seconds(host: str) -> float:
    return WIKIMEDIA_DELAY_SECONDS if host.endswith(WIKIMEDIA_HOST_SUFFIX) else DEFAULT_HOST_DELAY_SECONDS


def build_data_uri_with_retries(
    url: str,
    timeout: int,
    host_deadlines: dict[str, float],
    retries: int = DEFAULT_IMAGE_RETRIES,
) -> str:
    host = urllib.parse.urlparse(url).netloc
    last_error: Exception | None = None
    for attempt in range(retries):
        wait_for_host(host, host_deadlines, host_delay_seconds(host))
        try:
            return build_data_uri(url, timeout)
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code == 429 and attempt + 1 < retries:
                retry_after = exc.headers.get("Retry-After")
                sleep_seconds = (
                    float(retry_after)
                    if retry_after and retry_after.isdigit()
                    else max(15.0, 20.0 * (attempt + 1))
                )
                time.sleep(sleep_seconds)
                continue
            raise
        except (urllib.error.URLError, ValueError, TimeoutError) as exc:
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            raise
    assert last_error is not None
    raise last_error


def inline_remote_images(html: str, timeout: int, cache_dir: Path) -> str:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache: dict[str, str] = {}
    host_deadlines: dict[str, float] = {}
    pattern = re.compile(r'(<img[^>]+src=")((?:https?:)?//[^\"]+)(")')
    urls = list(dict.fromkeys(match.group(2) for match in pattern.finditer(html)))
    failures: list[str] = []

    def fetch_into_cache(url: str) -> bool:
        asset_cache_path = cache_path_for_url(cache_dir, url)
        if asset_cache_path.exists():
            cache[url] = asset_cache_path.read_text(encoding="utf-8")
            return True
        try:
            cache[url] = build_data_uri_with_retries(url, timeout, host_deadlines)
            asset_cache_path.write_text(cache[url], encoding="utf-8")
            return True
        except (urllib.error.URLError, ValueError, TimeoutError) as exc:
            print(f"Warning: could not inline image {url}: {exc}", file=sys.stderr)
            return False

    for url in urls:
        if not fetch_into_cache(url):
            failures.append(url)

    if failures:
        time.sleep(30)
        remaining_failures: list[str] = []
        for url in failures:
            if not fetch_into_cache(url):
                remaining_failures.append(url)
        failures = remaining_failures

    def replace(match: re.Match[str]) -> str:
        prefix, url, suffix = match.groups()
        return f'{prefix}{cache.get(url, url)}{suffix}'

    return pattern.sub(replace, html)


def execute_notebook(notebook, notebook_path: Path, kernel_name: str | None, timeout: int, allow_errors: bool, execute_preprocessor) -> None:
    executor = execute_preprocessor(
        timeout=timeout,
        kernel_name=kernel_name,
        allow_errors=allow_errors,
    )
    executor.preprocess(
        notebook,
        resources={"metadata": {"path": str(notebook_path.parent)}},
    )


def export_html(notebook, notebook_path: Path, html_exporter) -> str:
    exporter = html_exporter(template_name="lab")
    exporter.anchor_link_text = ""
    exporter.embed_images = True
    exporter.exclude_input = True
    exporter.exclude_input_prompt = True
    exporter.exclude_output_prompt = True
    body, _resources = exporter.from_notebook_node(
        notebook,
        resources={"metadata": {"name": notebook_path.stem, "path": str(notebook_path.parent)}},
    )
    return body


def render_pdf(html_path: Path, pdf_path: Path, browser_path: str, time_budget_ms: int) -> None:
    command = [
        browser_path,
        "--headless",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--hide-scrollbars",
        "--allow-file-access-from-files",
        "--run-all-compositor-stages-before-draw",
        f"--virtual-time-budget={time_budget_ms}",
        "--print-to-pdf-no-header",
        f"--print-to-pdf={pdf_path}",
        html_path.resolve().as_uri(),
    ]
    if sys.platform.startswith("linux"):
        command.insert(1, "--no-sandbox")

    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        detail = stderr or stdout or f"browser exited with status {result.returncode}"
        raise RuntimeError(f"PDF render failed: {detail}")


def default_output_path(notebook_path: Path) -> Path:
    return notebook_path.with_name(f"{notebook_path.stem}.paper.pdf")


def extract_title(notebook) -> str | None:
    """Return the text of the first level-1 markdown heading, if any."""
    for cell in notebook.cells:
        if cell.get("cell_type") != "markdown":
            continue
        for line in cell.get("source", "").splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                return re.sub(r"\s+", " ", stripped[2:].strip()) or None
    return None


def set_document_title(html: str, title: str | None) -> str:
    """Replace the exported <title> so PDF metadata shows the paper title."""
    if not title:
        return html
    safe = (
        title.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    if "<title>" in html:
        return re.sub(r"<title>.*?</title>", f"<title>{safe}</title>", html, count=1, flags=re.S)
    return html.replace("</head>", f"<title>{safe}</title>\n</head>", 1)


def resolve_output_path(notebook_path: Path, args: argparse.Namespace, batch: bool) -> Path:
    if args.output and not batch:
        return Path(args.output).expanduser().resolve()
    if args.output_dir:
        out_dir = Path(args.output_dir).expanduser().resolve()
        return out_dir / f"{notebook_path.stem}.paper.pdf"
    return default_output_path(notebook_path)


def render_one(
    notebook_path: Path,
    output_path: Path,
    args: argparse.Namespace,
    browser_path: str,
    cache_dir: Path,
    tools,
) -> None:
    nbformat, html_exporter, execute_preprocessor = tools
    output_path.parent.mkdir(parents=True, exist_ok=True)

    notebook = nbformat.read(notebook_path, as_version=4)
    kernel_name = args.kernel_name or notebook.metadata.get("kernelspec", {}).get("name")

    if not args.skip_execute:
        print(f"Executing {notebook_path.name} ...", file=sys.stderr)
        execute_notebook(
            notebook,
            notebook_path,
            kernel_name,
            args.timeout,
            args.allow_errors,
            execute_preprocessor,
        )

    title = extract_title(notebook)
    html = export_html(notebook, notebook_path, html_exporter)
    html = inline_remote_images(html, timeout=DEFAULT_IMAGE_TIMEOUT, cache_dir=cache_dir)
    html = inject_print_styles(html, args.page_size)
    html = set_document_title(html, title)

    if args.html_output:
        html_path = Path(args.html_output).expanduser().resolve()
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(html, encoding="utf-8")
        render_pdf(html_path, output_path, browser_path, args.virtual_time_budget_ms)
    else:
        with tempfile.TemporaryDirectory(prefix="notebook-paper-") as tmp_dir:
            html_path = Path(tmp_dir) / f"{notebook_path.stem}.print.html"
            html_path.write_text(html, encoding="utf-8")
            render_pdf(html_path, output_path, browser_path, args.virtual_time_budget_ms)


def main() -> int:
    args = parse_args()

    requested = args.notebooks or list(DEFAULT_NOTEBOOKS)
    batch = len(requested) > 1

    if args.output and batch:
        print(
            "Warning: --output is ignored when rendering multiple notebooks; "
            "use --output-dir instead.",
            file=sys.stderr,
        )
    if args.html_output and batch:
        raise SystemExit("--html-output is only valid when rendering a single notebook.")

    notebook_paths = []
    for entry in requested:
        path = Path(entry).expanduser()
        if not path.is_absolute():
            path = (Path.cwd() / path).resolve()
        else:
            path = path.resolve()
        if not path.exists():
            raise FileNotFoundError(f"Notebook not found: {path}")
        notebook_paths.append(path)

    browser_path = resolve_browser(args.browser)
    tools = load_notebook_tools()

    # A shared cache lets both papers reuse the same president/minister photos.
    cache_dir = Path.cwd() / "tmp" / "paper-image-cache"

    generated: list[Path] = []
    for notebook_path in notebook_paths:
        output_path = resolve_output_path(notebook_path, args, batch)
        render_one(notebook_path, output_path, args, browser_path, cache_dir, tools)
        generated.append(output_path)
        print(f"  ✓ {notebook_path.name} → {output_path}", file=sys.stderr)

    print("\nGenerated PDF paper(s):", file=sys.stderr)
    for path in generated:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())