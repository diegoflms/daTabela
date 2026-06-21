from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import get_row_by_id, list_games, list_rows, list_rows_by_foreign_id

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("")
def list_teams(
    db: Annotated[Session, Depends(get_db)],
    q: Annotated[str | None, Query(description="Busca por nome ou slug do time.")] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    return list_rows(
        db,
        "teams",
        search_columns=("name", "slug", "city", "state"),
        search=q,
        order_by=("name", "id"),
        limit=limit,
        offset=offset,
    )


@router.get("/{team_id}")
def get_team(
    team_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    team = get_row_by_id(db, "teams", team_id)

    if team is None:
        raise HTTPException(status_code=404, detail="Time não encontrado.")

    return team


@router.get("/{team_id}/seasons")
def get_team_seasons(
    team_id: int,
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    if get_row_by_id(db, "teams", team_id) is None:
        raise HTTPException(status_code=404, detail="Time não encontrado.")

    return list_rows_by_foreign_id(
        db,
        "team_seasons",
        "team_id",
        team_id,
        order_by=("season_id", "id"),
        limit=limit,
        offset=offset,
    )


@router.get("/{team_id}/games")
def get_team_games(
    team_id: int,
    db: Annotated[Session, Depends(get_db)],
    season_id: Annotated[int | None, Query(description="Filtra jogos do time por temporada.")] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    if get_row_by_id(db, "teams", team_id) is None:
        raise HTTPException(status_code=404, detail="Time não encontrado.")

    return list_games(
        db,
        season_id=season_id,
        team_id=team_id,
        limit=limit,
        offset=offset,
    )