import csv
import re
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.models.table_specs import FINAL_TABLE_SPECS, TableSpec


INTEGER_HINTS = {
    "id",
    "season_id",
    "team_id",
    "home_team_id",
    "away_team_id",
    "opponent_team_id",
    "player_id",
    "game_id",
    "rank",
    "wins",
    "losses",
    "games",
    "games_played",
    "start_year",
    "end_year",
    "year",
    "jersey_number",
    "is_current",
    "is_champion",
}

REAL_KEYWORDS = (
    "pct",
    "percentage",
    "percent",
    "avg",
    "average",
    "per_game",
    "rating",
    "eff",
    "efficiency",
    "minutes",
    "min",
)


def quote_identifier(identifier: str) -> str:
    cleaned = identifier.replace('"', '""')
    return f'"{cleaned}"'


def normalize_column_name(column_name: str) -> str:
    normalized = column_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9_]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized)
    return normalized.strip("_")


def infer_sqlite_type(column_name: str) -> str:
    name = normalize_column_name(column_name)

    if name in INTEGER_HINTS or name.endswith("_id"):
        return "INTEGER"

    if any(keyword in name for keyword in REAL_KEYWORDS):
        return "REAL"

    return "TEXT"


def read_csv_header(csv_path: Path) -> list[str]:
    with csv_path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        header = next(reader, [])

    columns = [normalize_column_name(column) for column in header if column.strip()]

    if not columns:
        raise ValueError(f"CSV sem cabeçalho válido: {csv_path}")

    if len(columns) != len(set(columns)):
        duplicates = sorted({column for column in columns if columns.count(column) > 1})
        raise ValueError(f"CSV com colunas duplicadas após normalização: {csv_path} -> {duplicates}")

    return columns


def build_create_table_sql(spec: TableSpec, columns: list[str]) -> str:
    column_defs: list[str] = []

    for column in columns:
        sqlite_type = infer_sqlite_type(column)

        if spec.primary_key and column == spec.primary_key:
            column_defs.append(f"{quote_identifier(column)} INTEGER PRIMARY KEY")
        else:
            column_defs.append(f"{quote_identifier(column)} {sqlite_type}")

    joined_columns = ",\n    ".join(column_defs)

    return f"""
CREATE TABLE IF NOT EXISTS {quote_identifier(spec.table_name)} (
    {joined_columns}
)
""".strip()


def build_index_sql(spec: TableSpec, columns: list[str]) -> list[str]:
    existing_columns = set(columns)
    statements: list[str] = []

    for column in spec.index_columns:
        if column not in existing_columns:
            continue

        index_name = f"idx_{spec.table_name}_{column}"

        statements.append(
            f"CREATE INDEX IF NOT EXISTS {quote_identifier(index_name)} "
            f"ON {quote_identifier(spec.table_name)} ({quote_identifier(column)})"
        )

    return statements


def create_schema_from_csv_headers(
    engine: Engine,
    data_dir: Path,
    *,
    drop_existing: bool = False,
) -> dict[str, dict[str, object]]:
    summary: dict[str, dict[str, object]] = {}

    with engine.begin() as connection:
        for spec in FINAL_TABLE_SPECS:
            csv_path = data_dir / spec.csv_file

            if not csv_path.exists():
                summary[spec.table_name] = {
                    "status": "missing_csv",
                    "csv_path": str(csv_path),
                    "columns": [],
                    "indexes": 0,
                }
                continue

            columns = read_csv_header(csv_path)

            if drop_existing:
                connection.execute(text(f"DROP TABLE IF EXISTS {quote_identifier(spec.table_name)}"))

            connection.execute(text(build_create_table_sql(spec, columns)))

            index_statements = build_index_sql(spec, columns)

            for statement in index_statements:
                connection.execute(text(statement))

            summary[spec.table_name] = {
                "status": "created",
                "csv_path": str(csv_path),
                "columns": columns,
                "indexes": len(index_statements),
            }

    return summary