# core/db_health.py

from __future__ import annotations

import argparse
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence

from core import db


CheckStatus = Literal["PASS", "FAIL", "INFO"]

REQUIRED_SCHEMA: dict[str, frozenset[str]] = {
    "tasks": frozenset(
        {
            "id",
            "title",
            "priority",
            "due_date",
            "status",
            "created_at",
            "updated_at",
            "queue",
            "waiting_reason",
        }
    ),
    "notes": frozenset(
        {
            "id",
            "title",
            "body",
            "tags",
            "created_at",
            "updated_at",
            "task_id",
        }
    ),
    "task_notes": frozenset(
        {
            "id",
            "task_id",
            "body",
            "created_at",
            "time_spent_minutes",
        }
    ),
}


@dataclass(frozen=True)
class HealthCheckResult:
    status: CheckStatus
    name: str
    details: str = ""


def _connect_read_only(
    database_path: Path,
) -> sqlite3.Connection:
    database_uri = (
        f"{database_path.resolve().as_uri()}?mode=ro"
    )

    connection = sqlite3.connect(
        database_uri,
        uri=True,
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")

    return connection


def _get_table_names(
    connection: sqlite3.Connection,
) -> set[str]:
    rows = connection.execute(
        """
        SELECT name
        FROM sqlite_schema
        WHERE type = 'table';
        """
    ).fetchall()

    return {
        str(row["name"])
        for row in rows
    }


def _get_column_names(
    connection: sqlite3.Connection,
    table_name: str,
) -> set[str]:
    # table_name comes only from REQUIRED_SCHEMA.
    rows = connection.execute(
        f'PRAGMA table_info("{table_name}");'
    ).fetchall()

    return {
        str(row["name"])
        for row in rows
    }


def check_database(
    database_path: Path | str,
) -> list[HealthCheckResult]:
    path = Path(database_path)
    results: list[HealthCheckResult] = []

    if not path.exists():
        return [
            HealthCheckResult(
                status="FAIL",
                name="Database file exists",
                details=f"Not found: {path}",
            )
        ]

    if not path.is_file():
        return [
            HealthCheckResult(
                status="FAIL",
                name="Database file exists",
                details=f"Path is not a file: {path}",
            )
        ]

    results.append(
        HealthCheckResult(
            status="PASS",
            name="Database file exists",
            details=str(path),
        )
    )

    try:
        connection = _connect_read_only(path)
    except sqlite3.Error as exc:
        results.append(
            HealthCheckResult(
                status="FAIL",
                name="Database opened successfully",
                details=str(exc),
            )
        )
        return results

    results.append(
        HealthCheckResult(
            status="PASS",
            name="Database opened successfully",
        )
    )

    try:
        table_names = _get_table_names(connection)
        missing_tables = sorted(
            set(REQUIRED_SCHEMA) - table_names
        )

        if missing_tables:
            results.append(
                HealthCheckResult(
                    status="FAIL",
                    name="Required tables are present",
                    details=(
                        f"Missing: {', '.join(missing_tables)}"
                    ),
                )
            )
        else:
            results.append(
                HealthCheckResult(
                    status="PASS",
                    name="Required tables are present",
                )
            )

            missing_columns: dict[str, list[str]] = {}

            for (
                table_name,
                required_columns,
            ) in REQUIRED_SCHEMA.items():
                existing_columns = _get_column_names(
                    connection,
                    table_name,
                )

                missing = sorted(
                    required_columns - existing_columns
                )

                if missing:
                    missing_columns[table_name] = missing

            if missing_columns:
                details = "; ".join(
                    (
                        f"{table}: "
                        f"{', '.join(columns)}"
                    )
                    for table, columns
                    in missing_columns.items()
                )

                results.append(
                    HealthCheckResult(
                        status="FAIL",
                        name="Required columns are present",
                        details=details,
                    )
                )
            else:
                results.append(
                    HealthCheckResult(
                        status="PASS",
                        name="Required columns are present",
                    )
                )

        quick_check_rows = connection.execute(
            "PRAGMA quick_check;"
        ).fetchall()

        quick_check_messages = [
            str(row[0])
            for row in quick_check_rows
        ]

        if quick_check_messages == ["ok"]:
            results.append(
                HealthCheckResult(
                    status="PASS",
                    name=(
                        "SQLite quick check returned OK"
                    ),
                )
            )
        else:
            results.append(
                HealthCheckResult(
                    status="FAIL",
                    name=(
                        "SQLite quick check returned OK"
                    ),
                    details="; ".join(
                        quick_check_messages
                    ),
                )
            )

        foreign_key_rows = connection.execute(
            "PRAGMA foreign_key_check;"
        ).fetchall()

        if foreign_key_rows:
            results.append(
                HealthCheckResult(
                    status="FAIL",
                    name=(
                        "No foreign-key violations found"
                    ),
                    details=(
                        f"Found "
                        f"{len(foreign_key_rows)} "
                        f"violation(s)"
                    ),
                )
            )
        else:
            results.append(
                HealthCheckResult(
                    status="PASS",
                    name=(
                        "No foreign-key violations found"
                    ),
                )
            )

        version_row = connection.execute(
            "PRAGMA user_version;"
        ).fetchone()

        schema_version = (
            int(version_row[0])
            if version_row
            else 0
        )

        version_details = str(schema_version)

        if schema_version == 0:
            version_details += " (unversioned)"

        results.append(
            HealthCheckResult(
                status="INFO",
                name="Schema version",
                details=version_details,
            )
        )

    except sqlite3.Error as exc:
        results.append(
            HealthCheckResult(
                status="FAIL",
                name="Database checks completed",
                details=str(exc),
            )
        )
    finally:
        connection.close()

    return results


def is_healthy(
    results: Sequence[HealthCheckResult],
) -> bool:
    return all(
        result.status != "FAIL"
        for result in results
    )


def print_report(
    database_path: Path | str,
    results: Sequence[HealthCheckResult],
) -> None:
    print("Boardroom database health check")
    print(f"Database: {Path(database_path)}")
    print()

    for result in results:
        details = (
            f": {result.details}"
            if result.details
            else ""
        )

        print(
            f"[{result.status}] "
            f"{result.name}"
            f"{details}"
        )

    print()

    if is_healthy(results):
        print("Database health check passed.")
    else:
        print("Database health check failed.")

    print("No changes were made.")


def main(
    argv: Sequence[str] | None = None,
) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run read-only health checks against "
            "Boardroom's SQLite database."
        )
    )

    parser.add_argument(
        "database",
        nargs="?",
        type=Path,
        default=db.DB_PATH,
        help=(
            "SQLite database path "
            f"(default: {db.DB_PATH})"
        ),
    )

    args = parser.parse_args(argv)

    results = check_database(args.database)
    print_report(args.database, results)

    return 0 if is_healthy(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())