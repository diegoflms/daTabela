from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import get_row_by_id, list_player_games, list_rows, list_rows_by_foreign_id

router = APIRouter(prefix="/players", tags=["players"])


@router.get("")
def list_players(
    db: Annotated[Session, Depends(get_db)],
    q: Annotated[str | None, Query(description="Busca por nome ou slug do jogador.")] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    from sqlalchemy import text
    from app.repositories import clamp_pagination
    limit, offset = clamp_pagination(limit, offset)

    where_parts = []
    params = {}

    if q:
        where_parts.append("(p.display_name LIKE :q OR p.full_name LIKE :q OR p.slug LIKE :q)")
        params["q"] = f"%{q}%"

    where_sql = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""

    params["limit"] = limit
    params["offset"] = offset

    statement = text(
        f"""
        SELECT p.*, 
               ps.primary_team_id AS current_team_id, 
               t.canonical_name AS current_team_name,
               t.logo_url AS current_team_logo_url
        FROM players p
        INNER JOIN player_seasons ps ON ps.player_id = p.id AND ps.season_id = 18
        INNER JOIN teams t ON t.id = ps.primary_team_id
        {where_sql}
        ORDER BY p.display_name ASC, p.full_name ASC, p.id ASC
        LIMIT :limit OFFSET :offset
        """
    )
    
    rows = [dict(row) for row in db.execute(statement, params).mappings().all()]

    count_statement = text(
        f"""
        SELECT COUNT(*)
        FROM players p
        INNER JOIN player_seasons ps ON ps.player_id = p.id AND ps.season_id = 18
        {where_sql}
        """
    )
    count_params = {k: v for k, v in params.items() if k not in {"limit", "offset"}}
    total = int(db.execute(count_statement, count_params).scalar_one())

    return {
        "items": rows,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{player_id}")
def get_player(
    player_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    from sqlalchemy import text
    statement = text(
        """
        SELECT p.*, 
               ps.primary_team_id AS current_team_id, 
               t.canonical_name AS current_team_name,
               t.logo_url AS current_team_logo_url
        FROM players p
        LEFT JOIN player_seasons ps ON ps.player_id = p.id AND ps.season_id = 18
        LEFT JOIN teams t ON t.id = ps.primary_team_id
        WHERE p.id = :player_id
        LIMIT 1
        """
    )
    row = db.execute(statement, {"player_id": player_id}).mappings().first()

    if row is None:
        raise HTTPException(status_code=404, detail="Jogador não encontrado.")

    return dict(row)


@router.get("/{player_id}/seasons")
def get_player_seasons(
    player_id: int,
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=1000)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    if get_row_by_id(db, "players", player_id) is None:
        raise HTTPException(status_code=404, detail="Jogador não encontrado.")

    return list_rows_by_foreign_id(
        db,
        "player_seasons",
        "player_id",
        player_id,
        order_by=("season_id", "id"),
        limit=limit,
        offset=offset,
    )


@router.get("/{player_id}/games")
def get_player_games(
    player_id: int,
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=1000)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    if get_row_by_id(db, "players", player_id) is None:
        raise HTTPException(status_code=404, detail="Jogador não encontrado.")

    return list_player_games(
        db,
        player_id,
        limit=limit,
        offset=offset,
    )


@router.get("/{player_id}/records")
def get_player_records(
    player_id: int,
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=1000)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    if get_row_by_id(db, "players", player_id) is None:
        raise HTTPException(status_code=404, detail="Jogador não encontrado.")

    return list_rows_by_foreign_id(
        db,
        "player_records",
        "player_id",
        player_id,
        order_by=("scope", "record_type", "id"),
        limit=limit,
        offset=offset,
    )