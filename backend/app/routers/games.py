from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import get_row_by_id, list_game_stats, list_games

router = APIRouter(prefix="/games", tags=["games"])


@router.get("")
def list_games_route(
    db: Annotated[Session, Depends(get_db)],
    season_id: Annotated[int | None, Query(description="Filtra jogos por temporada.")] = None,
    team_id: Annotated[int | None, Query(description="Filtra jogos em que o time participou.")] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    return list_games(
        db,
        season_id=season_id,
        team_id=team_id,
        limit=limit,
        offset=offset,
    )


@router.get("/{game_id}")
def get_game(
    game_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    game = get_row_by_id(db, "games", game_id)

    if game is None:
        raise HTTPException(status_code=404, detail="Jogo não encontrado.")

    return game


@router.get("/{game_id}/player-stats")
def get_game_player_stats(
    game_id: int,
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=200)] = 200,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    if get_row_by_id(db, "games", game_id) is None:
        raise HTTPException(status_code=404, detail="Jogo não encontrado.")

    return list_game_stats(
        db,
        "player_game_stats",
        game_id,
        limit=limit,
        offset=offset,
    )


@router.get("/{game_id}/team-stats")
def get_game_team_stats(
    game_id: int,
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    if get_row_by_id(db, "games", game_id) is None:
        raise HTTPException(status_code=404, detail="Jogo não encontrado.")

    return list_game_stats(
        db,
        "team_game_stats",
        game_id,
        limit=limit,
        offset=offset,
    )