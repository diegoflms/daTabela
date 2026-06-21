from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import list_rows

router = APIRouter(prefix="/standings", tags=["standings"])


@router.get("")
def list_standings(
    db: Annotated[Session, Depends(get_db)],
    season_id: Annotated[int | None, Query(description="Filtra classificação por temporada.")] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    return list_rows(
        db,
        "standings",
        filters={"season_id": season_id},
        order_by=("season_id", "rank", "position", "id"),
        limit=limit,
        offset=offset,
    )