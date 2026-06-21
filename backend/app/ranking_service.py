from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.repositories import clamp_pagination, get_table_columns, table_exists
from app.schema import quote_identifier
from app.stat_metrics import GAMES_COLUMN_CANDIDATES, MetricSpec


def _resolve_metric_column(columns: set[str], metric: MetricSpec) -> str | None:
    for candidate in metric.column_candidates:
        if candidate in columns:
            return candidate

    return None


def available_metrics(
    db: Session,
    table_name: str,
    metric_specs: tuple[MetricSpec, ...],
) -> list[dict[str, str]]:
    columns = get_table_columns(db, table_name)

    available: list[dict[str, str]] = []

    for metric in metric_specs:
        resolved_column = _resolve_metric_column(columns, metric)

        if resolved_column:
            available.append(
                {
                    "key": metric.key,
                    "label": metric.label,
                    "column": resolved_column,
                }
            )

    return available


def resolve_metric(
    db: Session,
    table_name: str,
    metric_key: str,
    metric_specs: tuple[MetricSpec, ...],
) -> tuple[MetricSpec | None, str | None]:
    columns = get_table_columns(db, table_name)

    for metric in metric_specs:
        if metric.key != metric_key:
            continue

        return metric, _resolve_metric_column(columns, metric)

    return None, None


def _resolve_games_column(columns: set[str]) -> str | None:
    for candidate in GAMES_COLUMN_CANDIDATES:
        if candidate in columns:
            return candidate

    return None


def _build_optional_join(
    db: Session,
    base_table: str,
    base_columns: set[str],
) -> tuple[str, list[str]]:
    joins: list[str] = []
    extra_selects: list[str] = []

    if "player_id" in base_columns and table_exists(db, "players"):
        player_columns = get_table_columns(db, "players")
        joins.append('LEFT JOIN "players" AS p ON p."id" = base."player_id"')

        if "display_name" in player_columns:
            extra_selects.append('p."display_name" AS player_name')
        elif "name" in player_columns:
            extra_selects.append('p."name" AS player_name')
        elif "full_name" in player_columns:
            extra_selects.append('p."full_name" AS player_name')

        if "photo_url" in player_columns:
            extra_selects.append('p."photo_url" AS player_photo_url')

        if "slug" in player_columns:
            extra_selects.append('p."slug" AS player_slug')

    # Check if we should join the teams table
    team_join_col = None
    if "team_id" in base_columns:
        team_join_col = "team_id"
    elif "primary_team_id" in base_columns:
        team_join_col = "primary_team_id"

    if team_join_col and table_exists(db, "teams"):
        team_columns = get_table_columns(db, "teams")
        joins.append(f'LEFT JOIN "teams" AS t ON t."id" = base."{team_join_col}"')

        if "canonical_name" in team_columns:
            extra_selects.append('t."canonical_name" AS team_name')
        elif "name" in team_columns:
            extra_selects.append('t."name" AS team_name')

        if "logo_url" in team_columns:
            extra_selects.append('t."logo_url" AS team_logo_url')

        if "slug" in team_columns:
            extra_selects.append('t."slug" AS team_slug')

        extra_selects.append('t."id" AS team_id')

    return " ".join(joins), extra_selects


def rank_table_by_metric(
    db: Session,
    table_name: str,
    metric_column: str,
    *,
    season_id: int | None = None,
    team_id: int | None = None,
    min_games: int = 0,
    limit: int = 50,
    offset: int = 0,
    higher_is_better: bool = True,
) -> dict[str, Any]:
    limit, offset = clamp_pagination(limit, offset)

    if not table_exists(db, table_name):
        return {
            "items": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
        }

    columns = get_table_columns(db, table_name)
    games_column = _resolve_games_column(columns)

    where_parts: list[str] = []
    params: dict[str, Any] = {}

    if season_id is not None and "season_id" in columns:
        where_parts.append('base."season_id" = :season_id')
        params["season_id"] = season_id

    if team_id is not None:
        if "team_id" in columns:
            where_parts.append('base."team_id" = :team_id')
            params["team_id"] = team_id
        elif "primary_team_id" in columns:
            where_parts.append('base."primary_team_id" = :team_id')
            params["team_id"] = team_id

    if min_games > 0 and games_column:
        where_parts.append(f'CAST(base.{quote_identifier(games_column)} AS REAL) >= :min_games')
        params["min_games"] = min_games

    where_parts.append(f'base.{quote_identifier(metric_column)} IS NOT NULL')
    where_parts.append(f'base.{quote_identifier(metric_column)} != ""')

    where_sql = f"WHERE {' AND '.join(where_parts)}"

    join_sql, extra_selects = _build_optional_join(db, table_name, columns)
    extra_select_sql = ""

    if extra_selects:
        extra_select_sql = ", " + ", ".join(extra_selects)

    direction = "DESC" if higher_is_better else "ASC"

    params["limit"] = limit
    params["offset"] = offset

    statement = text(
        f"""
        SELECT
            base.*,
            CAST(base.{quote_identifier(metric_column)} AS REAL) AS ranking_value
            {extra_select_sql}
        FROM {quote_identifier(table_name)} AS base
        {join_sql}
        {where_sql}
        ORDER BY ranking_value {direction}
        LIMIT :limit OFFSET :offset
        """
    )

    rows = [
        dict(row)
        for row in db.execute(statement, params).mappings().all()
    ]

    count_params = {
        key: value
        for key, value in params.items()
        if key not in {"limit", "offset"}
    }

    count_statement = text(
        f"""
        SELECT COUNT(*)
        FROM {quote_identifier(table_name)} AS base
        {where_sql}
        """
    )

    total = int(db.execute(count_statement, count_params).scalar_one())

    return {
        "items": rows,
        "total": total,
        "limit": limit,
        "offset": offset,
    }