# core/migrations.py

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping


Migration = Callable[[sqlite3.Connection], None]

# Keys represent the destination schema version.
#
# Example after the first real schema change:
#
# MIGRATIONS = {
#     2: migrate_to_version_2,
# }
MIGRATIONS: dict[int, Migration] = {}


class MigrationError(RuntimeError):
    """Raised when a database migration cannot complete safely."""


class MissingMigrationError(MigrationError):
    """Raised when the ordered migration path has a gap."""


class MigrationBackupError(MigrationError):
    """Raised when a pre-migration backup cannot be created."""


@dataclass(frozen=True)
class MigrationRunResult:
    starting_version: int
    ending_version: int
    applied_versions: tuple[int, ...]
    backup_path: Path | None


def get_schema_version(
    connection: sqlite3.Connection,
) -> int:
    row = connection.execute(
        "PRAGMA user_version;"
    ).fetchone()

    return int(row[0]) if row else 0


def set_schema_version(
    connection: sqlite3.Connection,
    version: int,
) -> None:
    version = int(version)

    if version < 0:
        raise ValueError(
            "Schema version cannot be negative."
        )

    connection.execute(
        f"PRAGMA user_version = {version};"
    )


def get_pending_versions(
    current_version: int,
    target_version: int,
) -> tuple[int, ...]:
    current_version = int(current_version)
    target_version = int(target_version)

    if current_version < 0 or target_version < 0:
        raise ValueError(
            "Schema versions cannot be negative."
        )

    if current_version > target_version:
        raise MigrationError(
            f"Database schema version {current_version} "
            f"is newer than target version "
            f"{target_version}."
        )

    return tuple(
        range(
            current_version + 1,
            target_version + 1,
        )
    )


def get_missing_migration_versions(
    current_version: int,
    target_version: int,
    migrations: Mapping[int, Migration],
) -> tuple[int, ...]:
    return tuple(
        version
        for version in get_pending_versions(
            current_version,
            target_version,
        )
        if version not in migrations
    )


def _unique_backup_path(
    candidate: Path,
) -> Path:
    if not candidate.exists():
        return candidate

    counter = 1

    while True:
        alternate = candidate.with_name(
            f"{candidate.stem}-{counter}"
            f"{candidate.suffix}"
        )

        if not alternate.exists():
            return alternate

        counter += 1


def _validate_database_integrity(
    connection: sqlite3.Connection,
) -> None:
    quick_check = [
        str(row[0])
        for row in connection.execute(
            "PRAGMA quick_check;"
        ).fetchall()
    ]

    if quick_check != ["ok"]:
        raise MigrationError(
            "SQLite quick check failed: "
            + "; ".join(quick_check)
        )

    foreign_key_violations = connection.execute(
        "PRAGMA foreign_key_check;"
    ).fetchall()

    if foreign_key_violations:
        raise MigrationError(
            "Foreign-key check found "
            f"{len(foreign_key_violations)} "
            "violation(s)."
        )


def create_database_backup(
    source_connection: sqlite3.Connection,
    database_path: Path | str,
    *,
    next_version: int,
    backup_dir: Path | str | None = None,
    now: datetime | None = None,
) -> Path:
    source_path = Path(database_path)

    if not source_path.is_file():
        raise MigrationBackupError(
            "Cannot back up missing database: "
            f"{source_path}"
        )

    destination_dir = (
        Path(backup_dir)
        if backup_dir is not None
        else source_path.parent / "backups"
    )

    try:
        destination_dir.mkdir(
            parents=True,
            exist_ok=True,
        )
    except OSError as exc:
        raise MigrationBackupError(
            "Could not create backup directory: "
            f"{exc}"
        ) from exc

    timestamp_source = (
        now
        or datetime.now(timezone.utc)
    )

    if timestamp_source.tzinfo is None:
        timestamp_source = (
            timestamp_source.replace(
                tzinfo=timezone.utc
            )
        )

    timestamp = (
        timestamp_source
        .astimezone(timezone.utc)
        .strftime("%Y%m%dT%H%M%S%fZ")
    )

    candidate = destination_dir / (
        f"{source_path.stem}"
        f"-before-v{int(next_version)}"
        f"-{timestamp}"
        f"{source_path.suffix or '.db'}"
    )

    backup_path = _unique_backup_path(
        candidate
    )

    try:
        with sqlite3.connect(
            backup_path
        ) as backup_connection:
            source_connection.backup(
                backup_connection
            )

            _validate_database_integrity(
                backup_connection
            )

    except (
        sqlite3.Error,
        MigrationError,
    ) as exc:
        try:
            backup_path.unlink(
                missing_ok=True
            )
        except OSError:
            pass

        raise MigrationBackupError(
            "Could not create a valid "
            f"database backup: {exc}"
        ) from exc

    return backup_path


def run_pending_migrations(
    connection: sqlite3.Connection,
    database_path: Path | str,
    *,
    target_version: int,
    migrations: (
        Mapping[int, Migration] | None
    ) = None,
    backup_dir: Path | str | None = None,
    now: datetime | None = None,
) -> MigrationRunResult:
    if connection.in_transaction:
        raise MigrationError(
            "Migration runner requires a "
            "connection with no active transaction."
        )

    migration_map = (
        MIGRATIONS
        if migrations is None
        else migrations
    )

    starting_version = get_schema_version(
        connection
    )

    pending_versions = get_pending_versions(
        starting_version,
        target_version,
    )

    if not pending_versions:
        return MigrationRunResult(
            starting_version=starting_version,
            ending_version=starting_version,
            applied_versions=(),
            backup_path=None,
        )

    missing_versions = (
        get_missing_migration_versions(
            starting_version,
            target_version,
            migration_map,
        )
    )

    if missing_versions:
        formatted = ", ".join(
            str(version)
            for version in missing_versions
        )

        raise MissingMigrationError(
            "Missing migration(s) for "
            f"version(s): {formatted}."
        )

    backup_path = create_database_backup(
        connection,
        database_path,
        next_version=pending_versions[0],
        backup_dir=backup_dir,
        now=now,
    )

    applied_versions: list[int] = []

    for version in pending_versions:
        migration = migration_map[version]

        try:
            connection.execute(
                "BEGIN IMMEDIATE;"
            )

            migration(connection)

            _validate_database_integrity(
                connection
            )

            set_schema_version(
                connection,
                version,
            )

            connection.commit()

        except Exception as exc:
            connection.rollback()

            remaining_version = (
                get_schema_version(
                    connection
                )
            )

            raise MigrationError(
                f"Migration to version "
                f"{version} failed. "
                f"Database remains at version "
                f"{remaining_version}. "
                f"Backup: {backup_path}"
            ) from exc

        applied_versions.append(version)

    return MigrationRunResult(
        starting_version=starting_version,
        ending_version=get_schema_version(
            connection
        ),
        applied_versions=tuple(
            applied_versions
        ),
        backup_path=backup_path,
    )