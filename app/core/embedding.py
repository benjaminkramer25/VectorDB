import numpy as np
from uuid import UUID
from typing import List

# --------------  dummy embed for local tests  --------------
def embed(text: str) -> List[float]:
    """Tiny deterministic embedding: character counts."""
    vec = np.zeros(26)
    for ch in text.lower():
        if ch.isalpha():
            vec[ord(ch) - 97] += 1
    return vec.tolist()

# ---- in real tests, swap out with Cohere / OpenAI call ----
async def batch_embed(chunks: list[tuple[UUID, str]]) -> dict[UUID, List[float]]:
    return {cid: embed(txt) for cid, txt in chunks}
