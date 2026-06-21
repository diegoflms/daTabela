from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.ranking_service import available_metrics, rank_table_by_metric, resolve_metric
from app.stat_metrics import PLAYER_METRICS, TEAM_METRICS

router = APIRouter(prefix="/rankings", tags=["rankings"])


@router.get("/players/metrics")
def list_player_ranking_metrics(
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    return {
        "table": "player_seasons",
        "metrics": available_metrics(db, "player_seasons", PLAYER_METRICS),
    }


@router.get("/teams/metrics")
def list_team_ranking_metrics(
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    return {
        "table": "team_seasons",
        "metrics": available_metrics(db, "team_seasons", TEAM_METRICS),
    }


@router.get("/players/{metric}")
def rank_players(
    metric: str,
    db: Annotated[Session, Depends(get_db)],
    season_id: Annotated[int | None, Query(description="Filtra ranking por temporada.")] = None,
    team_id: Annotated[int | None, Query(description="Filtra ranking por time quando a tabela permitir.")] = None,
    min_games: Annotated[int, Query(ge=0, description="Mínimo de jogos para entrar no ranking.")] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    metric_spec, metric_column = resolve_metric(db, "player_seasons", metric, PLAYER_METRICS)

    if metric_spec is None or metric_column is None:
        available = available_metrics(db, "player_seasons", PLAYER_METRICS)
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Métrica de jogador indisponível.",
                "requested_metric": metric,
                "available_metrics": available,
            },
        )

    result = rank_table_by_metric(
        db,
        "player_seasons",
        metric_column,
        season_id=season_id,
        team_id=team_id,
        min_games=min_games,
        limit=limit,
        offset=offset,
        higher_is_better=metric_spec.higher_is_better,
    )

    result["metric"] = {
        "key": metric_spec.key,
        "label": metric_spec.label,
        "column": metric_column,
    }

    return result


@router.get("/teams/{metric}")
def rank_teams(
    metric: str,
    db: Annotated[Session, Depends(get_db)],
    season_id: Annotated[int | None, Query(description="Filtra ranking por temporada.")] = None,
    min_games: Annotated[int, Query(ge=0, description="Mínimo de jogos para entrar no ranking.")] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    metric_spec, metric_column = resolve_metric(db, "team_seasons", metric, TEAM_METRICS)

    if metric_spec is None or metric_column is None:
        available = available_metrics(db, "team_seasons", TEAM_METRICS)
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Métrica de time indisponível.",
                "requested_metric": metric,
                "available_metrics": available,
            },
        )

    result = rank_table_by_metric(
        db,
        "team_seasons",
        metric_column,
        season_id=season_id,
        min_games=min_games,
        limit=limit,
        offset=offset,
        higher_is_better=metric_spec.higher_is_better,
    )

    result["metric"] = {
        "key": metric_spec.key,
        "label": metric_spec.label,
        "column": metric_column,
    }

    return result