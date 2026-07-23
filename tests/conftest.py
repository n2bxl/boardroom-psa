# tests/conftest.py
from __future__ import annotations

import pytest

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import core.db as db

@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    test_db_path = tmp_path / "test_life.db"
    monkeypatch.setattr(db, "DB_PATH", test_db_path)
    db.init_db()
    return test_db_path