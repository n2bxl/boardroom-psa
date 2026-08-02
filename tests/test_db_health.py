# tests/test_db_health.py

from __future__ import annotations

import sqlite3

from core.db_health import (
    REQUIRED_SCHEMA,
    HealthCheckResult,
    check_database,
    is_healthy,
    main,
)


def _result_for(
    results: list[HealthCheckResult],
    name: str,
) -> HealthCheckResult:
    return next(
        result
        for result in results
        if result.name == name
    )


def test_healthy_database_passes_required_checks(
    temp_db,
):
    results = check_database(temp_db)

    assert is_healthy(results)

    assert (
        _result_for(
            results,
            "Required tables are present",
        ).status
        == "PASS"
    )

    assert (
        _result_for(
            results,
            "Required columns are present",
        ).status
        == "PASS"
    )

    assert (
        _result_for(
            results,
            "SQLite quick check returned OK",
        ).status
        == "PASS"
    )

    assert (
        _result_for(
            results,
            "No foreign-key violations found",
        ).status
        == "PASS"
    )

    assert (
        _result_for(
            results,
            "Schema version",
        ).details
        == "0 (unversioned)"
    )


def test_missing_required_table_fails_health_check(
    tmp_path,
):
    database_path = tmp_path / "missing_table.db"

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE tasks (
                id INTEGER PRIMARY KEY
            );
            """
        )

    results = check_database(database_path)

    table_result = _result_for(
        results,
        "Required tables are present",
    )

    assert not is_healthy(results)
    assert table_result.status == "FAIL"
    assert "notes" in table_result.details
    assert "task_notes" in table_result.details


def test_missing_required_column_fails_health_check(
    tmp_path,
):
    database_path = tmp_path / "missing_column.db"

    with sqlite3.connect(database_path) as connection:
        for (
            table_name,
            required_columns,
        ) in REQUIRED_SCHEMA.items():
            columns = sorted(required_columns)

            if table_name == "notes":
                columns.remove("tags")

            column_sql = ", ".join(
                f'"{column_name}" TEXT'
                for column_name in columns
            )

            connection.execute(
                f"""
                CREATE TABLE "{table_name}" (
                    {column_sql}
                );
                """
            )

    results = check_database(database_path)

    column_result = _result_for(
        results,
        "Required columns are present",
    )

    assert not is_healthy(results)
    assert column_result.status == "FAIL"
    assert "notes: tags" in column_result.details


def test_foreign_key_violation_fails_health_check(
    temp_db,
):
    with sqlite3.connect(temp_db) as connection:
        connection.execute(
            "PRAGMA foreign_keys = OFF;"
        )

        connection.execute(
            """
            INSERT INTO task_notes (
                task_id,
                body,
                created_at,
                time_spent_minutes
            )
            VALUES (
                999,
                'Orphaned worklog',
                '2026-08-01T20:00:00Z',
                5
            );
            """
        )

    results = check_database(temp_db)

    foreign_key_result = _result_for(
        results,
        "No foreign-key violations found",
    )

    assert not is_healthy(results)
    assert foreign_key_result.status == "FAIL"
    assert "1 violation" in foreign_key_result.details


def test_health_check_does_not_modify_database(
    temp_db,
):
    before = temp_db.read_bytes()

    check_database(temp_db)

    after = temp_db.read_bytes()

    assert after == before


def test_main_returns_expected_exit_codes(
    temp_db,
    tmp_path,
    capsys,
):
    assert main([str(temp_db)]) == 0

    healthy_output = capsys.readouterr().out

    assert (
        "Database health check passed."
        in healthy_output
    )
    assert "No changes were made." in healthy_output

    missing_path = tmp_path / "missing.db"

    assert main([str(missing_path)]) == 1

    unhealthy_output = capsys.readouterr().out

    assert (
        "Database health check failed."
        in unhealthy_output
    )

    # Read-only mode must not create a missing database.
    assert not missing_path.exists()