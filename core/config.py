# core/config.py
from __future__ import annotations

APP = {
    "title": "Boardroom",
    "page_icon": "🏛️",
    "layout": "wide"
}

DEFAULTS = { # TODO: complete AI integrations
    # LLM
    "ollama_model": "llama3.2:latest",
    "llm_temperature": 0.2,
    "llm_max_tokens": 512,

    # UI sizes
    "ai_context_height": 220,
    "ticket_note_height": 120,
    "note_body_height": 180,

    # Filters
    "default_queues": "ALL",
    "default_statuses": "OPEN",

    # Tabs
    "tabs": ["Board", "Notes", "Settings"],

    # Age + Staleness
    "stale_days_threshold": 3,
    "show_age_stale_columns": True,

    # Time
    "timezone_override": "",
    "use_system_timezone": True,
}