from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import list_rows

router = APIRouter(prefix="/seasons", tags=["seasons"])


@router.get("")
def list_seasons(
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    return list_rows(
        db,
        "seasons",
        order_by=("start_year", "id"),
        limit=limit,
        offset=offset,
    )