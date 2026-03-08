# ui/text_utils.py

from __future__ import annotations

def preview_text(text: str, limit: int) -> str:
    if not text:
        return ""
    text = text.strip().replace("\n", " ")
    return text[:limit] + "..." if len(text) > limit else text