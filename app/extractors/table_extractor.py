"""
app/extractors/table_extractor.py
---------------------------------
Fast, in-memory table extractor that:
1. Keyword-scans PDF with PyMuPDF   (cheap)
2. Uses LayoutPDFReader to get page indices
3. Slices table pages into a tiny PDF
4. Runs Docling only on that slice
"""

import os
import tempfile
import re
from typing import List, Dict, Any

import fitz  # PyMuPDF
from llmsherpa.readers import LayoutPDFReader
from docling.document_converter import DocumentConverter
from docling.datamodel.document import TableItem, DoclingDocument

# ---------------------------------------------------------------------
# End-point configuration
# ---------------------------------------------------------------------
LLMSHERPA_URL = os.getenv(
    "LLMSHERPA_URL",
    "http://localhost:5010/api/parseDocument?renderFormat=all"
)

_reader = LayoutPDFReader(LLMSHERPA_URL)         # fast layout pass
_converter = DocumentConverter()  # heavy Docling pass


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def _contains_table_keyword(path: str) -> bool:
    """Very fast scan for the word 'table' in any page."""
    doc = fitz.open(path)
    for page in doc:
        if re.search(r"\btable\b", page.get_text(), re.IGNORECASE):
            return True
    return False


def _get_table_page_indices(path: str) -> List[int]:
    """LLMSherpa → unique, sorted zero-based page indices with tables."""
    doc = _reader.read_pdf(path)
    return sorted({tbl.page_idx for tbl in doc.tables()})


def _slice_pages(src_path: str, page_indices: List[int]) -> bytes:
    """Return a new PDF (bytes) containing only the specified pages."""
    if not page_indices:
        return b""

    src = fitz.open(src_path)
    dst = fitz.open()               # empty PDF

    for idx in page_indices:
        if 0 <= idx < len(src):
            dst.insert_pdf(src, from_page=idx, to_page=idx)

    return dst.tobytes()            # -> bytes in memory


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------
def extract_tables_from_bytes(pdf_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Rapidly extract tables; skips heavy Docling if none detected.
    Returns an empty list if no tables exist.
    """
    # -------------------------------------------------
    # 1. Write original PDF to a temp file (reader needs path)
    # -------------------------------------------------
    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp_orig:
        tmp_orig.write(pdf_bytes)
        tmp_orig.flush()
        orig_path = tmp_orig.name

        # 1a. Cheap keyword filter
        if not _contains_table_keyword(orig_path):
            return []

        # 1b. Sherpa layout → page indices
        table_pages = _get_table_page_indices(orig_path)
        if not table_pages:
            return []

        # -------------------------------------------------
        # 2. Slice pages into an in-memory PDF
        # -------------------------------------------------
        sliced_pdf_bytes = _slice_pages(orig_path, table_pages)
        if not sliced_pdf_bytes:
            return []

        # -------------------------------------------------
        # 3. Run Docling on the tiny slice
        #    (needs its own temp file for path-based API)
        # -------------------------------------------------
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp_slice:
            tmp_slice.write(sliced_pdf_bytes)
            tmp_slice.flush()
            doc: DoclingDocument = _converter.convert(tmp_slice.name).document

    # -------------------------------------------------
    # 4. Harvest tables → plain dicts
    # -------------------------------------------------
    tables: List[TableItem] = doc.tables
    result: List[Dict[str, Any]] = []

    for idx, tbl in enumerate(tables, start=1):
        # Caption
        try:
            caption = tbl.caption_text(doc)
        except Exception:
            caption = None

        # Grid rows
        rows = [[cell.text for cell in row] for row in (tbl.data.grid or [])]

        # Footnotes
        foots = []
        if tbl.footnotes:
            for ref in tbl.footnotes:
                try:
                    foots.append(ref.resolve(doc).text)
                except Exception:
                    foots.append("[unresolved]")

        result.append(
            {
                "table_index": idx,
                "caption": caption,
                "rows": rows,
                "footnotes": foots,
            }
        )

    return result
