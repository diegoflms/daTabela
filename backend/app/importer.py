import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine

from app.models.table_specs import FINAL_TABLE_SPECS, TableSpec
from app.schema import (
    create_schema_from_csv_headers,
    infer_sqlite_type,
    normalize_column_name,
    quote_identifier,
    read_csv_header,
)


@dataclass(frozen=True)
class ImportResult:
    table_name: str
    csv_file: str
    status: str
    rows_imported: int = 0
    columns: int = 0
    error: str | None = None


def convert_value(value: str | None, sqlite_type: str) -> Any:
    if value is None:
        return None

    cleaned = value.strip()

    if cleaned == "":
        return None

    if sqlite_type == "INTEGER":
        try:
            return int(float(cleaned.replace(",", ".")))
        except ValueError:
            return None

    if sqlite_type == "REAL":
        try:
            return float(cleaned.replace(",", "."))
        except ValueError:
            return None

    return cleaned


def _read_csv_rows(csv_path: Path, columns: list[str]) -> list[dict[str, Any]]:
    column_types = {column: infer_sqlite_type(column) for column in columns}
    rows: list[dict[str, Any]] = []

    with csv_path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for raw_row in reader:
            normalized_row: dict[str, Any] = {}

            for original_column, raw_value in raw_row.items():
                if original_column is None:
                    continue

                column = normalize_column_name(original_column)

                if column not in columns:
                    continue

                normalized_row[column] = convert_value(raw_value, column_types[column])

            rows.append({column: normalized_row.get(column) for column in columns})

    return rows


def _insert_rows(
    connection: Connection,
    table_name: str,
    columns: list[str],
    rows: list[dict[str, Any]],
    *,
    batch_size: int,
) -> int:
    if not rows:
        return 0

    quoted_columns = ", ".join(quote_identifier(column) for column in columns)
    placeholders = ", ".join(f":{column}" for column in columns)

    statement = text(
        f"INSERT INTO {quote_identifier(table_name)} "
        f"({quoted_columns}) VALUES ({placeholders})"
    )

    total = 0

    for start in range(0, len(rows), batch_size):
        batch = rows[start:start + batch_size]
        connection.execute(statement, batch)
        total += len(batch)

    return total


def import_table(
    connection: Connection,
    spec: TableSpec,
    data_dir: Path,
    *,
    clear_existing: bool = True,
    batch_size: int = 1000,
) -> ImportResult:
    csv_path = data_dir / spec.csv_file

    if not csv_path.exists():
        return ImportResult(
            table_name=spec.table_name,
            csv_file=spec.csv_file,
            status="missing_csv",
            error=f"CSV não encontrado: {csv_path}",
        )

    try:
        columns = read_csv_header(csv_path)

        if clear_existing:
            connection.execute(text(f"DELETE FROM {quote_identifier(spec.table_name)}"))

        rows = _read_csv_rows(csv_path, columns)

        imported = _insert_rows(
            connection=connection,
            table_name=spec.table_name,
            columns=columns,
            rows=rows,
            batch_size=batch_size,
        )

        return ImportResult(
            table_name=spec.table_name,
            csv_file=spec.csv_file,
            status="imported",
            rows_imported=imported,
            columns=len(columns),
        )

    except Exception as exc:
        return ImportResult(
            table_name=spec.table_name,
            csv_file=spec.csv_file,
            status="error",
            error=str(exc),
        )


def import_all_csvs(
    engine: Engine,
    data_dir: Path,
    *,
    reset_schema: bool = True,
    batch_size: int = 1000,
) -> list[ImportResult]:
    if reset_schema:
        create_schema_from_csv_headers(
            engine=engine,
            data_dir=data_dir,
            drop_existing=True,
        )

    results: list[ImportResult] = []

    with engine.begin() as connection:
        for spec in FINAL_TABLE_SPECS:
            result = import_table(
                connection=connection,
                spec=spec,
                data_dir=data_dir,
                clear_existing=True,
                batch_size=batch_size,
            )
            results.append(result)

    return results


def get_table_counts(engine: Engine) -> dict[str, int]:
    counts: dict[str, int] = {}

    with engine.connect() as connection:
        for spec in FINAL_TABLE_SPECS:
            try:
                count = connection.execute(
                    text(f"SELECT COUNT(*) FROM {quote_identifier(spec.table_name)}")
                ).scalar_one()
                counts[spec.table_name] = int(count)
            except Exception:
                counts[spec.table_name] = -1

    return counts