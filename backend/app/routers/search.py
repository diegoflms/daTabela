from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.search_service import global_search, search_table

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
def search(
    db: Annotated[Session, Depends(get_db)],
    q: Annotated[str, Query(min_length=1, description="Texto buscado em jogadores, times, jogos e temporadas.")],
    limit: Annotated[int, Query(ge=1, le=50, description="Limite por grupo de resultado.")] = 10,
) -> dict[str, Any]:
    return global_search(
        db,
        query=q,
        limit=limit,
    )


@router.get("/players")
def search_players(
    db: Annotated[Session, Depends(get_db)],
    q: Annotated[str, Query(min_length=1, description="Texto buscado em jogadores.")],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    return search_table(
        db,
        "players",
        query=q,
        search_columns=("name", "full_name", "slug", "nickname", "birthplace", "position"),
        order_by=("name", "full_name", "id"),
        limit=limit,
        offset=offset,
    )


@router.get("/teams")
def search_teams(
    db: Annotated[Session, Depends(get_db)],
    q: Annotated[str, Query(min_length=1, description="Texto buscado em times.")],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    return search_table(
        db,
        "teams",
        query=q,
        search_columns=("name", "slug", "city", "state", "short_name", "abbreviation"),
        order_by=("name", "id"),
        limit=limit,
        offset=offset,
    )


@router.get("/games")
def search_games(
    db: Annotated[Session, Depends(get_db)],
    q: Annotated[str, Query(min_length=1, description="Texto buscado em jogos.")],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    return search_table(
        db,
        "games",
        query=q,
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
        offset=offset,
    )