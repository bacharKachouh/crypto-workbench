"""Convert PDF sources to text for downstream review / extraction.

The plugin treats the extracted `.md` file as the canonical reading
surface for agents. PDFs remain in the corpus as the authoritative
source; text extraction produces a best-effort plain-text companion
that agents (and the model) can Read without binary-decode failures.

Extraction is intentionally simple: page-by-page text, no OCR, no
layout reconstruction. Tables and figures will degrade. That is
acceptable — the impl spec flow is driven by prose sections.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


MODULE = "parsing.pdf_to_text"


class PdfExtractionError(RuntimeError):
    """Raised when a PDF cannot be read or the PDF dependency is missing."""


def extract_pdf_text(pdf_path: Path | str) -> str:
    """Extract plain text from a PDF file, page by page.

    Returns the concatenated text with page separators. Raises
    PdfExtractionError with an actionable message if pypdf is not
    installed or the file is unreadable.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise PdfExtractionError(f"PDF not found: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise PdfExtractionError(f"Not a .pdf file: {pdf_path}")

    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise PdfExtractionError(
            "pypdf is not installed. Install with `pip install pypdf` "
            "or ask the user to extract the PDF text manually into a .md "
            "file under corpus/papers/."
        ) from exc

    try:
        reader = PdfReader(str(pdf_path))
    except Exception as exc:
        raise PdfExtractionError(f"Could not open {pdf_path}: {exc}") from exc

    pages: list[str] = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        pages.append(f"<!-- page {i} -->\n{text.strip()}")

    return "\n\n".join(pages).strip() + "\n"


def write_extracted_text(
    pdf_path: Path | str,
    *,
    out_path: Path | str | None = None,
    front_matter: bool = True,
) -> Path:
    """Extract and write a companion .md next to the PDF.

    Default output: same stem as the PDF with `.md` suffix in the same
    directory. Overrides with `out_path`. Existing files are overwritten
    (caller is responsible for versioning if needed).
    """
    pdf_path = Path(pdf_path)
    if out_path is None:
        out_path = pdf_path.with_suffix(".md")
    out_path = Path(out_path)

    text = extract_pdf_text(pdf_path)

    header = ""
    if front_matter:
        header = (
            "<!--\n"
            f"extracted_from: {pdf_path.name}\n"
            "extractor: pypdf\n"
            "note: best-effort plain-text extraction; tables/figures may be degraded.\n"
            "-->\n\n"
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(header + text, encoding="utf-8")
    return out_path


def run(**context: Any) -> dict[str, Any]:
    """Workflow entry point: extract every PDF in corpus/papers/ + corpus/standards/.

    Returns the list of written companion .md paths.
    """
    corpus_root = Path(context.get("corpus_root", ".cryptoworkbench/corpus"))
    written: list[str] = []
    skipped: list[dict[str, str]] = []

    for subdir in ("papers", "standards", "fetched"):
        d = corpus_root / subdir
        if not d.exists():
            continue
        for pdf in sorted(d.glob("*.pdf")):
            try:
                out = write_extracted_text(pdf)
                written.append(str(out))
            except PdfExtractionError as exc:
                skipped.append({"path": str(pdf), "reason": str(exc)})

    return {
        "module": MODULE,
        "status": "extracted" if written else "noop",
        "written": written,
        "skipped": skipped,
    }
