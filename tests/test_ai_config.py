# tests/test_ai_config.py

from __future__ import annotations

from core.ai import make_llm


def test_make_llm_applies_generation_settings():
    llm = make_llm(
        model="gpt-oss:20b",
        temperature=0.35,
        max_tokens=640,
    )

    assert llm.model == "gpt-oss:20b"
    assert llm.temperature == 0.35
    assert llm.num_predict == 640