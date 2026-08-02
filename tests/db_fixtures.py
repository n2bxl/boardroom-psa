# tests/db_fixtures.py

from __future__ import annotations

import sqlite3
from pathlib import Path


def build_versioned_database(
    database_path: Path,
    *,
    version: int = 1,
) -> Path:
    """
    Build a small reviewable database fixture
    for migration-runner tests.
    """
    with sqlite3.connect(
        database_path
    ) as connection:
        connection.execute(
            """
            CREATE TABLE migration_probe (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT NOT NULL
            );
            """
        )

        connection.execute(
            """
            INSERT INTO migration_probe (label)
            VALUES ('baseline');
            """
        )

        connection.execute(
            f"PRAGMA user_version = "
            f"{int(version)};"
        )

    return database_path