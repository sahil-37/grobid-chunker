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