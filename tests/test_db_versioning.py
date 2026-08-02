# tests/test_db_versioning.py

from __future__ import annotations

import pytest

import core.db as db


def test_new_database_receives_current_schema_version(
    temp_db,
):
    with db.get_conn() as connection:
        version = db.get_schema_version(
            connection
        )

    assert version == db.CURRENT_SCHEMA_VERSION


def test_unversioned_database_is_adopted_without_data_loss(
    temp_db,
):
    task_id = db.add_task(
        title="Preserve this task",
        priority="High",
        due_date=None,
    )

    with db.get_conn() as connection:
        db.set_schema_version(
            connection,
            0,
        )

    db.init_db()

    with db.get_conn() as connection:
        version = db.get_schema_version(
            connection
        )

    task = db.get_task(task_id)

    assert version == db.CURRENT_SCHEMA_VERSION
    assert task is not None
    assert task.title == "Preserve this task"
    assert task.priority == "High"


def test_current_database_is_not_reversioned(
    temp_db,
    monkeypatch,
):
    def unexpected_version_write(
        connection,
        version,
    ):
        raise AssertionError(
            "Current database should not be "
            "versioned again."
        )

    monkeypatch.setattr(
        db,
        "set_schema_version",
        unexpected_version_write,
    )

    db.init_db()


def test_newer_database_version_is_rejected(
    temp_db,
):
    newer_version = (
        db.CURRENT_SCHEMA_VERSION + 1
    )

    with db.get_conn() as connection:
        db.set_schema_version(
            connection,
            newer_version,
        )

    with pytest.raises(
        db.UnsupportedDatabaseVersionError,
        match="newer",
    ):
        db.init_db()

    with db.get_conn() as connection:
        stored_version = db.get_schema_version(
            connection
        )

    assert stored_version == newer_version


def test_malformed_unversioned_database_is_not_adopted(
    tmp_path,
    monkeypatch,
):
    database_path = (
        tmp_path / "malformed.db"
    )

    monkeypatch.setattr(
        db,
        "DB_PATH",
        database_path,
    )

    with db.get_conn() as connection:
        connection.execute(
            """
            CREATE TABLE tasks (
                id INTEGER PRIMARY KEY,
                created_at TEXT
            );
            """
        )

    with pytest.raises(
        db.DatabaseSchemaError,
        match="tasks missing columns",
    ):
        db.init_db()

    with db.get_conn() as connection:
        version = db.get_schema_version(
            connection
        )

    assert version == 0