from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database import engine


def first_id(table_name: str) -> int | None:
    with engine.connect() as connection:
        result = connection.execute(
            text(f'SELECT id FROM "{table_name}" ORDER BY id LIMIT 1')
        ).first()

    if result is None:
        return None

    return int(result[0])


def row_count(table_name: str) -> int | None:
    with engine.connect() as connection:
        try:
            result = connection.execute(
                text(f'SELECT COUNT(*) FROM "{table_name}"')
            ).scalar_one()
        except Exception:
            return None

    return int(result)


def assert_paginated_payload(data: dict[str, Any]) -> None:
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert isinstance(data["items"], list)
    assert isinstance(data["total"], int)
    assert isinstance(data["limit"], int)
    assert isinstance(data["offset"], int)


def assert_paginated_endpoint(client: TestClient, path: str) -> dict[str, Any]:
    response = client.get(path)

    assert response.status_code == 200

    data = response.json()
    assert_paginated_payload(data)

    return data