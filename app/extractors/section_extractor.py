from __future__ import annotations
from typing import Any, List, Dict
from lxml import etree

from app.models import (
    NS, RESULTS_ANCHORS, DISCUSSION_ANCHORS, DISCUSSION_STOPWORDS,
    ABSTRACT_ALTERNATES, MERGED_RESULTS_DISCUSSION_ANCHORS
)
from app.utils.tei_helpers import _clean, _div_heading
from app.utils.semantic_utils import is_semantic_heading_match

STOPWORD_SIM_THRESHOLD = 0.65  # adjust if needed

def extract_structured_sections(xml_str: str) -> Dict[str, Any]:
    try:
        tree = etree.fromstring(xml_str.encode())
    except Exception:
        return {}

    divs = tree.xpath(".//tei:body//tei:div", namespaces=NS)

    # ─────────────── Title
    title = _clean(tree.xpath("string(.//tei:titleStmt/tei:title)", namespaces=NS))

    # ─────────────── Abstract
    abstract = [
        _clean("".join(p.itertext()))
        for p in tree.xpath(".//tei:abstract//tei:p", namespaces=NS)
        if _clean("".join(p.itertext()))
    ]
    abstract_heading = "abstract"
    if not abstract:
        for d in divs:
            head = _div_heading(d)
            if head and is_semantic_heading_match(head, ABSTRACT_ALTERNATES):
                abstract = [
                    _clean("".join(p.itertext()))
                    for p in d.xpath(".//tei:p", namespaces=NS)
                    if _clean("".join(p.itertext()))
                ]
                abstract_heading = head
                break

    # ─────────────── Results + Discussion Section
    def extract_results_discussion() -> Dict[str, Any]:
        capturing = False
        matched_heading: str | None = None
        sections: Dict[str, List[str]] = {}
        subheadings: List[str] = []
        unnamed_count = 0

        for d in divs:
            head = _div_heading(d)
            head_lower = head.lower().strip() if head else ""

            # 🚫 Hard stop — exact or semantic stopword match
            if head and (
                head_lower in DISCUSSION_STOPWORDS or
                is_semantic_heading_match(head, DISCUSSION_STOPWORDS, threshold=STOPWORD_SIM_THRESHOLD)
            ):
                break

            # ✅ Start capturing after matching result/discussion heading
            if not capturing and head and (
                is_semantic_heading_match(head, MERGED_RESULTS_DISCUSSION_ANCHORS, token_level=True)
                or is_semantic_heading_match(head, RESULTS_ANCHORS, token_level=True)
                or is_semantic_heading_match(head, DISCUSSION_ANCHORS, token_level=True)
            ):
                capturing = True
                matched_heading = head

            if not capturing:
                continue

            # 🔎 Track section heading or assign fallback
            section_heading = head if head else f"unnamed_section_{unnamed_count}"
            if head:
                subheadings.append(section_heading)
            else:
                unnamed_count += 1

            paragraphs = [
                _clean("".join(p.itertext()))
                for p in d.xpath(".//tei:p", namespaces=NS)
                if _clean("".join(p.itertext()))
            ]
            if paragraphs:
                sections[section_heading] = paragraphs

        return {
            "heading": "results_and_discussion",
            "matched_heading": matched_heading,
            "sections": sections,
            "subheadings": subheadings
        }

    # ─────────────── Final return
    return {
        "title": {"heading": "title", "content": title},
        "abstract": {"heading": abstract_heading, "content": abstract},
        "results_discussion": extract_results_discussion()
    }
