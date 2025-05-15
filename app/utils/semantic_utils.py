import re
from typing import Set
from sentence_transformers import util
from app.models import MODEL

WORD_RE = re.compile(r"[A-Za-z]+")

def is_semantic_heading_match(
    heading: str,
    anchor_set: Set[str],
    threshold: float = 0.9,
    token_level: bool = False
) -> bool:
    """
    Check if a heading semantically matches an anchor set.
    - If token_level is False: full string-to-set match
    - If token_level is True: any token-to-set match
    """
    if token_level:
        tokens = [token.lower() for token in WORD_RE.findall(heading)]
        if not tokens:
            return False
        keyword_embeds = MODEL.encode(sorted(anchor_set), convert_to_tensor=True)
        for token in tokens:
            token_emb = MODEL.encode(token, convert_to_tensor=True)
            sim = util.pytorch_cos_sim(token_emb, keyword_embeds)
            if sim.max().item() >= threshold:
                return True
        return False
    else:
        anchor_embeds = MODEL.encode(sorted(anchor_set), convert_to_tensor=True)
        heading_emb = MODEL.encode(heading, convert_to_tensor=True)
        sim = util.pytorch_cos_sim(heading_emb, anchor_embeds)
        return sim.max().item() >= threshold
