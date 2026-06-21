from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schema import quote_identifier


DEFAULT_LIMIT = 50
MAX_LIMIT = 1000


def clamp_pagination(limit: int, offset: int) -> tuple[int, int]:
    safe_limit = max(1, min(limit, MAX_LIMIT))
    safe_offset = max(0, offset)

    return safe_limit, safe_offset


def table_exists(db: Session, table_name: str) -> bool:
    statement = text(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name = :table_name
        """
    )

    result = db.execute(statement, {"table_name": table_name}).first()

    return result is not None


def get_table_columns(db: Session, table_name: str) -> set[str]:
    if not table_exists(db, table_name):
        return set()

    statement = text(f"PRAGMA table_info({quote_identifier(table_name)})")
    rows = db.execute(statement).mappings().all()

    return {str(row["name"]) for row in rows}


def count_rows(
    db: Session,
    table_name: str,
    filters: dict[str, Any] | None = None,
) -> int:
    if not table_exists(db, table_name):
        return 0

    filters = filters or {}
    columns = get_table_columns(db, table_name)

    where_parts: list[str] = []
    params: dict[str, Any] = {}

    for column, value in filters.items():
        if value is None:
            continue

        if column not in columns:
            continue

        where_parts.append(f"{quote_identifier(column)} = :{column}")
        params[column] = value

    where_sql = f" WHERE {' AND '.join(where_parts)}" if where_parts else ""

    statement = text(
        f"SELECT COUNT(*) FROM {quote_identifier(table_name)}{where_sql}"
    )

    return int(db.execute(statement, params).scalar_one())


def list_rows(
    db: Session,
    table_name: str,
    *,
    filters: dict[str, Any] | None = None,
    search_columns: tuple[str, ...] = (),
    search: str | None = None,
    order_by: tuple[str, ...] = ("id",),
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
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
    filters = filters or {}

    where_parts: list[str] = []
    params: dict[str, Any] = {}

    for column, value in filters.items():
        if value is None:
            continue

        if column not in columns:
            continue

        where_parts.append(f"{quote_identifier(column)} = :{column}")
        params[column] = value

    if search:
        search_parts: list[str] = []

        for column in search_columns:
            if column in columns:
                key = f"search_{column}"
                search_parts.append(f"LOWER({quote_identifier(column)}) LIKE LOWER(:{key})")
                params[key] = f"%{search}%"

        if search_parts:
            where_parts.append(f"({' OR '.join(search_parts)})")

    where_sql = f" WHERE {' AND '.join(where_parts)}" if where_parts else ""

    valid_order_columns = [column for column in order_by if column in columns]
    order_sql = ""

    if valid_order_columns:
        joined = ", ".join(quote_identifier(column) for column in valid_order_columns)
        order_sql = f" ORDER BY {joined}"

    params["limit"] = limit
    params["offset"] = offset

    statement = text(
        f"""
        SELECT *
        FROM {quote_identifier(table_name)}
        {where_sql}
        {order_sql}
        LIMIT :limit OFFSET :offset
        """
    )

    rows = [
        dict(row)
        for row in db.execute(statement, params).mappings().all()
    ]

    total = count_rows(db, table_name, filters)

    return {
        "items": rows,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


def get_row_by_id(
    db: Session,
    table_name: str,
    row_id: int,
) -> dict[str, Any] | None:
    if not table_exists(db, table_name):
        return None

    columns = get_table_columns(db, table_name)

    if "id" not in columns:
        return None

    statement = text(
        f"""
        SELECT *
        FROM {quote_identifier(table_name)}
        WHERE {quote_identifier("id")} = :row_id
        LIMIT 1
        """
    )

    row = db.execute(statement, {"row_id": row_id}).mappings().first()

    if row is None:
        return None

    return dict(row)


def list_rows_by_foreign_id(
    db: Session,
    table_name: str,
    column_name: str,
    value: int,
    *,
    order_by: tuple[str, ...] = ("id",),
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> dict[str, Any]:
    return list_rows(
        db,
        table_name,
        filters={column_name: value},
        order_by=order_by,
        limit=limit,
        offset=offset,
    )


def list_games(
    db: Session,
    *,
    season_id: int | None = None,
    team_id: int | None = None,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> dict[str, Any]:
    limit, offset = clamp_pagination(limit, offset)

    table_name = "games"

    if not table_exists(db, table_name):
        return {
            "items": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
        }

    columns = get_table_columns(db, table_name)

    where_parts: list[str] = []
    params: dict[str, Any] = {}

    if season_id is not None and "season_id" in columns:
        where_parts.append(f"{quote_identifier('season_id')} = :season_id")
        params["season_id"] = season_id

    team_filter_columns = [
        column
        for column in ("home_team_id", "away_team_id", "team_id")
        if column in columns
    ]

    if team_id is not None and team_filter_columns:
        team_parts = [
            f"{quote_identifier(column)} = :team_id"
            for column in team_filter_columns
        ]

        where_parts.append(f"({' OR '.join(team_parts)})")
        params["team_id"] = team_id

    where_sql = f" WHERE {' AND '.join(where_parts)}" if where_parts else ""

    order_sql = " ORDER BY game_date DESC, id DESC"

    params["limit"] = limit
    params["offset"] = offset

    statement = text(
        f"""
        SELECT *
        FROM {quote_identifier(table_name)}
        {where_sql}
        {order_sql}
        LIMIT :limit OFFSET :offset
        """
    )

    rows = [
        dict(row)
        for row in db.execute(statement, params).mappings().all()
    ]

    count_statement = text(
        f"SELECT COUNT(*) FROM {quote_identifier(table_name)}{where_sql}"
    )

    total_params = {
        key: value
        for key, value in params.items()
        if key not in {"limit", "offset"}
    }

    total = int(db.execute(count_statement, total_params).scalar_one())

    return {
        "items": rows,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


def list_player_games(
    db: Session,
    player_id: int,
    *,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> dict[str, Any]:
    limit, offset = clamp_pagination(limit, offset)
    statement = text(
        """
        SELECT pgs.*, 
               g.game_date, 
               g.home_team_id, 
               g.away_team_id, 
               g.home_score, 
               g.away_score, 
               g.home_team_name_raw, 
               g.away_team_name_raw, 
               g.winner_team_id
        FROM player_game_stats pgs
        LEFT JOIN games g ON g.id = pgs.game_id
        WHERE pgs.player_id = :player_id
        ORDER BY g.game_date DESC, g.game_time DESC, pgs.id DESC
        LIMIT :limit OFFSET :offset
        """
    )
    rows = [dict(row) for row in db.execute(statement, {"player_id": player_id, "limit": limit, "offset": offset}).mappings().all()]
    
    count_statement = text("SELECT COUNT(*) FROM player_game_stats WHERE player_id = :player_id")
    total = int(db.execute(count_statement, {"player_id": player_id}).scalar_one())
    
    return {
        "items": rows,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


def list_game_stats(
    db: Session,
    table_name: str,
    game_id: int,
    *,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> dict[str, Any]:
    return list_rows(
        db,
        table_name,
        filters={"game_id": game_id},
        order_by=("team_id", "player_id", "id"),
        limit=limit,
        offset=offset,
    )