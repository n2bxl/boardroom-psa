from __future__ import annotations

import streamlit as st

from core.config import APP, DEFAULTS
from core.constants import STATUS_ORDER, OPEN_STATUSES, QUEUES
from core.db import init_db
from core.version import __version__

from ui.sidebar import render_sidebar
from ui.board import render_board
from ui.notes import render_notes
from ui.settings import render_settings_tab


# --- Settings helpers ---
def get_setting(key: str):
    return st.session_state.get(key, DEFAULTS[key])


def init_settings():
    for k, v in DEFAULTS.items():
        st.session_state.setdefault(k, v)


def get_default_queues():
    v = get_setting("default_queues")
    return QUEUES if v == "ALL" else v


def get_default_statuses():
    v = get_setting("default_statuses")
    if v == "ALL":
        return STATUS_ORDER
    if v == "OPEN":
        return OPEN_STATUSES
    return v


# --- Tabs ---
def render_tabs():
    tab_names = get_setting("tabs")
    tabs = st.tabs(tab_names)

    registry = {
        "Board": lambda: render_board(
            model_name=get_setting("ollama_model"),
            get_default_statuses=get_default_statuses,
            get_default_queues=get_default_queues,
        ),
        "Notes": lambda: render_notes(),
        "Settings": lambda: render_settings_tab(get_setting),
    }

    for tab_obj, name in zip(tabs, tab_names):
        with tab_obj:
            registry[name]()


def main():
    init_db()
    init_settings()

    st.title(APP["title"])
    render_sidebar(get_setting)
    render_tabs()


st.set_page_config(page_title=APP["title"], page_icon=APP["page_icon"], layout=APP["layout"])

if __name__ == "__main__":
    main()