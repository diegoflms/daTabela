from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.repositories import clamp_pagination, get_table_columns, table_exists
from app.schema import quote_identifier


def _existing_columns(
    db: Session,
    table_name: str,
    candidates: tuple[str, ...],
) -> list[str]:
    columns = get_table_columns(db, table_name)

    return [
        column
        for column in candidates
        if column in columns
    ]


def search_table(
    db: Session,
    table_name: str,
    *,
    query: str,
    search_columns: tuple[str, ...],
    order_by: tuple[str, ...] = ("id",),
    limit: int = 10,
    offset: int = 0,
) -> dict[str, Any]:
    limit, offset = clamp_pagination(limit, offset)

    cleaned_query = query.strip()

    if not cleaned_query or not table_exists(db, table_name):
        return {
            "items": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
        }

    existing_search_columns = _existing_columns(db, table_name, search_columns)

    if not existing_search_columns:
        return {
            "items": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
        }

    columns = get_table_columns(db, table_name)
    params: dict[str, Any] = {
        "limit": limit,
        "offset": offset,
    }

    where_parts: list[str] = []

    for index, column in enumerate(existing_search_columns):
        key = f"q_{index}"
        where_parts.append(f"LOWER(CAST({quote_identifier(column)} AS TEXT)) LIKE LOWER(:{key})")
        params[key] = f"%{cleaned_query}%"

    where_sql = f"WHERE {' OR '.join(where_parts)}"

    existing_order_columns = [
        column
        for column in order_by
        if column in columns
    ]

    order_sql = ""

    if existing_order_columns:
        order_sql = "ORDER BY " + ", ".join(quote_identifier(column) for column in existing_order_columns)

    statement = text(
        f"""
        SELECT *
        FROM {quote_identifier(table_name)}
        {where_sql}
        {order_sql}
        LIMIT :limit OFFSET :offset
        """
    )

    count_params = {
        key: value
        for key, value in params.items()
        if key not in {"limit", "offset"}
    }

    count_statement = text(
        f"""
        SELECT COUNT(*)
        FROM {quote_identifier(table_name)}
        {where_sql}
        """
    )

    items = [
        dict(row)
        for row in db.execute(statement, params).mappings().all()
    ]

    total = int(db.execute(count_statement, count_params).scalar_one())

    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


def global_search(
    db: Session,
    *,
    query: str,
    limit: int = 10,
) -> dict[str, Any]:
    limit, _ = clamp_pagination(limit, 0)

    return {
        "query": query,
        "limit_per_group": limit,
        "players": search_table(
            db,
            "players",
            query=query,
            search_columns=("name", "full_name", "slug", "nickname", "birthplace", "position"),
            order_by=("name", "full_name", "id"),
            limit=limit,
        ),
        "teams": search_table(
            db,
            "teams",
            query=query,
            search_columns=("name", "slug", "city", "state", "short_name", "abbreviation"),
            order_by=("name", "id"),
            limit=limit,
        ),
        "games": search_table(
            db,
            "games",
            query=query,
            search_columns=(
                "game_date",
                "date",
                "phase",
                "stage",
                "round",
                "arena",
                "venue",
                "city",
                "home_team_name",
                "away_team_name",
                "boxscore_url",
                "source_url",
            ),
            order_by=("game_date", "date", "id"),
            limit=limit,
        ),
        "seasons": search_table(
            db,
            "seasons",
            query=query,
            search_columns=("name", "slug", "start_year", "end_year"),
            order_by=("start_year", "id"),
            limit=limit,
        ),
    }