import re
from typing import Any
from app.models import NS

def _clean(txt: str) -> str:
    return re.sub(r"\s+", " ", txt).strip()

def _div_heading(div: Any) -> str | None:
    return _clean(div.xpath("string(tei:head)", namespaces=NS)) or None

def _div_type_hint_okay(div: Any) -> bool:
    types = " ".join(div.attrib.values()).lower()
    return "method" in types or "material" in types


# regex to strip leading numbers, dots & whitespace
_LEADING_NUM_RE = re.compile(r"^\s*\d+(?:\.\d+)*[\.\)\:]?\s*")

def _normalize_heading(raw: str) -> str:
    """Remove any leading numbering (e.g. '3.1. Results' → 'Results')."""
    return _LEADING_NUM_RE.sub("", raw).strip()