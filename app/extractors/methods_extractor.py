from __future__ import annotations
from typing import Dict, List, Tuple
from lxml import etree

from app.models import ANCHORS, STOPWORDS, METHOD_KEYWORDS, NS
from app.utils.tei_helpers import _clean, _div_heading, _div_type_hint_okay
from app.utils.semantic_utils import is_semantic_heading_match

def extract_methods_with_subsections(
    xml_str: str,
    sim_threshold: float = 0.65,
    fallback_threshold: float = 0.5,
) -> Tuple[Dict[str, List[str]], float, str | None, int]:
    try:
        tree = etree.fromstring(xml_str.encode())
    except Exception:
        return {}, 0.0, None, -1

    divs = tree.xpath(".//tei:body//tei:div", namespaces=NS)
    if not divs:
        return {}, 0.0, None, -1

    result: Dict[str, List[str]] = {}
    start_head: str | None = None
    start_score: float = 0.0
    start_idx = None

    # Anchor mode
    for i, d in enumerate(divs):
        h = _div_heading(d)
        if h and is_semantic_heading_match(h, ANCHORS, sim_threshold):
            start_head = h
            start_score = 1.0
            start_idx = i
            break

    capturing = False
    current_subhead = None

    if start_idx is not None:
        capturing = True
        for d in divs[start_idx:]:
            h = _div_heading(d)
            if h and any(sw in h.lower() for sw in STOPWORDS):
                break
            if h:
                current_subhead = h
                result[current_subhead] = []
            for p in d.xpath(".//tei:p", namespaces=NS):
                t = _clean("".join(p.itertext()))
                if t:
                    result.setdefault(current_subhead or "untitled", []).append(t)

    else:
        for i, d in enumerate(divs):
            h = _div_heading(d)
            if not h and not _div_type_hint_okay(d):
                continue
            if h and any(sw in h.lower() for sw in STOPWORDS):
                if capturing:
                    break
                continue
            if _div_type_hint_okay(d) or (h and is_semantic_heading_match(h, METHOD_KEYWORDS, fallback_threshold, token_level=True)):
                if not capturing:
                    capturing = True
                    if h and not start_head:
                        start_head = h
                if h:
                    current_subhead = h
            if capturing:
                for p in d.xpath(".//tei:p", namespaces=NS):
                    t = _clean("".join(p.itertext()))
                    if t:
                        result.setdefault(current_subhead or "untitled", []).append(t)

        if not start_head:
            return {}, 0.0, None, -1

    return result, start_score, start_head, start_idx or -1
