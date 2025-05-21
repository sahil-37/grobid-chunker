import re
from typing import Any, List, Dict
from lxml import etree

from app.models import (
    NS,
    RESULTS_DISCUSSION_ANCHORS,
    RESULTS_STOPWORDS,
    DISCUSSION_STOPWORDS,
    ABSTRACT_ALTERNATES,
)
from app.utils.tei_helpers import _clean, _div_heading
from app.utils.semantic_utils import is_semantic_heading_match

# — strip leading numbering (e.g. “3.1. Results …” → “Results …”) for matching only
_LEADING_NUM_RE = re.compile(r"^\s*\d+(?:\.\d+)*[\.\)\:]?\s*")
def _norm_head(raw: str) -> str:
    return _LEADING_NUM_RE.sub("", raw).strip()

def extract_structured_sections(xml_str: str) -> Dict[str, Any]:
    try:
        tree = etree.fromstring(xml_str.encode())
    except Exception:
        return {}

    divs = tree.xpath(".//tei:body//tei:div", namespaces=NS)

    # ─── Title + Abstract ─────────────────────────────────────────────────────
    title = _clean(tree.xpath("string(.//tei:titleStmt/tei:title)", namespaces=NS))
    abstract = [
        _clean("".join(p.itertext()))
        for p in tree.xpath(".//tei:abstract//tei:p", namespaces=NS)
        if _clean("".join(p.itertext()))
    ]
    abstract_heading = "abstract"
    if not abstract:
        for d in divs:
            raw_h = _div_heading(d)
            h = _norm_head(raw_h) if raw_h else ""
            if h and is_semantic_heading_match(h, ABSTRACT_ALTERNATES):
                abstract = [
                    _clean("".join(p.itertext()))
                    for p in d.xpath(".//tei:p", namespaces=NS)
                    if _clean("".join(p.itertext()))
                ]
                abstract_heading = raw_h
                break

    # ─── Unified Results + Discussion ─────────────────────────────────────────
    def extract_unified_rd() -> Dict[str, Any]:
        anchors   = RESULTS_DISCUSSION_ANCHORS
        stopwords = RESULTS_STOPWORDS | DISCUSSION_STOPWORDS

        capturing = False
        main_heading: str | None = None
        subsections: List[Dict[str,Any]] = []
        current = {"subheading": None, "content": []}

        for d in divs:
            raw_h = _div_heading(d)               # e.g. "3. Results and discussion"
            h = _norm_head(raw_h) if raw_h else "" # → "Results and discussion"

            # 1) START if we hit any of the anchors
            if h and not capturing and is_semantic_heading_match(h, anchors, threshold =0.8):
                capturing = True
                main_heading = raw_h
                current = {"subheading": raw_h, "content": []}
                

            if capturing:
                # 2) STOP if we hit any stopword
                if h and is_semantic_heading_match(h, stopwords, token_level=True, threshold = 0.8):
                    break

                # 3) NEW SUBSECTION if a new head appears
                if raw_h:
                    if current["content"]:
                        subsections.append(current)
                    current = {"subheading": raw_h, "content": []}

                # 4) COLLECT paragraphs
                for p in d.xpath(".//tei:p", namespaces=NS):
                    txt = _clean("".join(p.itertext()))
                    if txt:
                        current["content"].append(txt)

        # flush last
        if capturing and current["content"]:
            subsections.append(current)

        return {
            "heading": main_heading or "results_and_discussion",
            "subsections": subsections
        }

    rd = extract_unified_rd()

    return {
        "title":    {"heading": "title",    "content": title},
        "abstract": {"heading": abstract_heading, "content": abstract},
        "results_discussion": rd
    }
