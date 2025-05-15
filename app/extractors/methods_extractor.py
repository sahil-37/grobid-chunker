from __future__ import annotations

import re
from typing import Any, List, Tuple
from lxml import etree

from app.models import MODEL, ANCHORS, STOPWORDS, METHOD_KEYWORDS, NS
from app.utils.tei_helpers import _clean, _div_heading, _div_type_hint_okay
from app.utils.semantic_utils import is_semantic_heading_match

def extract_methods_section(
    xml_str: str,
    sim_threshold: float = 0.65,
    fallback_threshold: float = 0.5,
) -> Tuple[List[str], List[str], float, str | None, int]:
    """
    Extract methods section from TEI XML using semantic heading matching.

    Returns:
        extracted_paragraphs, raw_paragraphs, start_score, start_heading, start_idx
    """
    try:
        tree = etree.fromstring(xml_str.encode())
    except Exception:
        return [], [], 0.0, None, -1

    divs = tree.xpath(".//tei:body//tei:div", namespaces=NS)
    if not divs:
        return [], [], 0.0, None, -1

    capturing = False
    stopped = False  # 🚨 Safety flag to skip divs after stop heading

    extracted_paragraphs = []
    raw_paragraphs = []
    start_heading: str | None = None
    start_score = 0.0
    start_idx = -1

    for i, div in enumerate(divs):
        if stopped:
            continue  # 🚨 Do not process anything after stopword section

        head = _div_heading(div)
        head_lower = head.lower() if head else ""

        # ───── Anchor Mode ─────
        if not capturing and head and is_semantic_heading_match(head, ANCHORS, sim_threshold):
            capturing = True
            start_heading = head
            start_score = 1.0
            start_idx = i

        # ───── Fallback ─────
        elif not capturing and (
            _div_type_hint_okay(div) or
            (head and is_semantic_heading_match(head, METHOD_KEYWORDS, fallback_threshold, token_level=True))
        ):
            capturing = True
            start_heading = head
            start_score = fallback_threshold
            start_idx = i

        if not capturing:
            continue

        # ───── Stop Condition ─────
        if head and any(sw in head_lower for sw in STOPWORDS):
            stopped = True
            continue  # Don't process this div or any after

        # ───── Paragraph Extraction ─────
        for p in div.xpath(".//tei:p", namespaces=NS):
            t = _clean("".join(p.itertext()))
            if t:
                extracted_paragraphs.append(t)
                raw_paragraphs.append(etree.tostring(p, encoding=str))

    return extracted_paragraphs, raw_paragraphs, start_score, start_heading, start_idx
