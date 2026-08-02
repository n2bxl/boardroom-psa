# tests/test_migrations.py

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

import pytest

from core.migrations import (
    MigrationBackupError,
    MigrationError,
    MissingMigrationError,
    create_database_backup,
    get_schema_version,
    run_pending_migrations,
)
from tests.db_fixtures import (
    build_versioned_database,
)


def test_migrations_run_in_order_and_create_backup(
    tmp_path,
):
    database_path = build_versioned_database(
        tmp_path / "life.db",
        version=1,
    )

    execution_order: list[int] = []

    def migrate_to_2(connection):
        execution_order.append(2)

        connection.execute(
            """
            INSERT INTO migration_probe (label)
            VALUES ('version 2');
            """
        )

    def migrate_to_3(connection):
        execution_order.append(3)

        previous = connection.execute(
            """
            SELECT COUNT(*)
            FROM migration_probe
            WHERE label = 'version 2';
            """
        ).fetchone()[0]

        assert previous == 1

        connection.execute(
            """
            INSERT INTO migration_probe (label)
            VALUES ('version 3');
            """
        )

    with sqlite3.connect(
        database_path
    ) as connection:
        result = run_pending_migrations(
            connection,
            database_path,
            target_version=3,
            migrations={
                2: migrate_to_2,
                3: migrate_to_3,
            },
            now=datetime(
                2026,
                8,
                2,
                2,
                0,
                tzinfo=timezone.utc,
            ),
        )

        labels = [
            row[0]
            for row in connection.execute(
                """
                SELECT label
                FROM migration_probe
                ORDER BY id;
                """
            ).fetchall()
        ]

    assert execution_order == [2, 3]
    assert result.starting_version == 1
    assert result.ending_version == 3
    assert result.applied_versions == (2, 3)

    assert result.backup_path is not None
    assert result.backup_path.exists()

    assert labels == [
        "baseline",
        "version 2",
        "version 3",
    ]

    with sqlite3.connect(
        result.backup_path
    ) as backup_connection:
        assert (
            get_schema_version(
                backup_connection
            )
            == 1
        )

        backup_labels = [
            row[0]
            for row
            in backup_connection.execute(
                """
                SELECT label
                FROM migration_probe
                ORDER BY id;
                """
            ).fetchall()
        ]

    assert backup_labels == ["baseline"]


def test_failed_migration_rolls_back_and_keeps_version(
    tmp_path,
):
    database_path = build_versioned_database(
        tmp_path / "life.db",
        version=1,
    )

    def failing_migration(connection):
        connection.execute(
            """
            INSERT INTO migration_probe (label)
            VALUES ('should roll back');
            """
        )

        raise RuntimeError(
            "simulated failure"
        )

    with sqlite3.connect(
        database_path
    ) as connection:
        with pytest.raises(
            MigrationError,
            match="version 2 failed",
        ):
            run_pending_migrations(
                connection,
                database_path,
                target_version=2,
                migrations={
                    2: failing_migration,
                },
            )

        assert (
            get_schema_version(connection)
            == 1
        )

        count = connection.execute(
            """
            SELECT COUNT(*)
            FROM migration_probe
            WHERE label = 'should roll back';
            """
        ).fetchone()[0]

    assert count == 0

    backups = list(
        (tmp_path / "backups")
        .glob("*.db")
    )

    assert len(backups) == 1


def test_current_database_does_not_create_backup(
    tmp_path,
):
    database_path = build_versioned_database(
        tmp_path / "life.db",
        version=1,
    )

    with sqlite3.connect(
        database_path
    ) as connection:
        result = run_pending_migrations(
            connection,
            database_path,
            target_version=1,
        )

    assert result.applied_versions == ()
    assert result.backup_path is None
    assert not (
        tmp_path / "backups"
    ).exists()


def test_missing_migration_aborts_before_backup(
    tmp_path,
):
    database_path = build_versioned_database(
        tmp_path / "life.db",
        version=1,
    )

    with sqlite3.connect(
        database_path
    ) as connection:
        with pytest.raises(
            MissingMigrationError,
            match=r"version\(s\): 3",
        ):
            run_pending_migrations(
                connection,
                database_path,
                target_version=3,
                migrations={
                    2: lambda conn: None,
                },
            )

    assert not (
        tmp_path / "backups"
    ).exists()


def test_backup_failure_prevents_migration(
    tmp_path,
    monkeypatch,
):
    database_path = build_versioned_database(
        tmp_path / "life.db",
        version=1,
    )

    migration_called = False

    def migration(connection):
        nonlocal migration_called
        migration_called = True

    def fail_backup(*args, **kwargs):
        raise MigrationBackupError(
            "simulated backup failure"
        )

    monkeypatch.setattr(
        "core.migrations."
        "create_database_backup",
        fail_backup,
    )

    with sqlite3.connect(
        database_path
    ) as connection:
        with pytest.raises(
            MigrationBackupError,
            match="simulated",
        ):
            run_pending_migrations(
                connection,
                database_path,
                target_version=2,
                migrations={
                    2: migration,
                },
            )

        assert (
            get_schema_version(connection)
            == 1
        )

    assert not migration_called


def test_backup_names_never_overwrite_existing_file(
    tmp_path,
):
    database_path = build_versioned_database(
        tmp_path / "life.db",
        version=1,
    )

    fixed_time = datetime(
        2026,
        8,
        2,
        2,
        0,
        tzinfo=timezone.utc,
    )

    with sqlite3.connect(
        database_path
    ) as connection:
        first = create_database_backup(
            connection,
            database_path,
            next_version=2,
            now=fixed_time,
        )

        second = create_database_backup(
            connection,
            database_path,
            next_version=2,
            now=fixed_time,
        )

    assert first.exists()
    assert second.exists()
    assert first != second