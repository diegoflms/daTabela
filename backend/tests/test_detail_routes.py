import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database import engine
from app.main import app

client = TestClient(app)


def get_first_id(table_name: str) -> int | None:
    with engine.connect() as connection:
        result = connection.execute(
            text(f'SELECT id FROM "{table_name}" ORDER BY id LIMIT 1')
        ).first()

    if result is None:
        return None

    return int(result[0])


def assert_paginated_response(path: str) -> None:
    response = client.get(path)

    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data


def test_player_detail_routes() -> None:
    player_id = get_first_id("players")

    if player_id is None:
        pytest.skip("Tabela players sem dados.")

    response = client.get(f"/players/{player_id}")

    assert response.status_code == 200
    assert response.json()["id"] == player_id

    assert_paginated_response(f"/players/{player_id}/seasons")
    assert_paginated_response(f"/players/{player_id}/games")


def test_team_detail_routes() -> None:
    team_id = get_first_id("teams")

    if team_id is None:
        pytest.skip("Tabela teams sem dados.")

    response = client.get(f"/teams/{team_id}")

    assert response.status_code == 200
    assert response.json()["id"] == team_id

    assert_paginated_response(f"/teams/{team_id}/seasons")
    assert_paginated_response(f"/teams/{team_id}/games")


def test_game_detail_routes() -> None:
    game_id = get_first_id("games")

    if game_id is None:
        pytest.skip("Tabela games sem dados.")

    response = client.get(f"/games/{game_id}")

    assert response.status_code == 200
    assert response.json()["id"] == game_id

    assert_paginated_response(f"/games/{game_id}/player-stats")
    assert_paginated_response(f"/games/{game_id}/team-stats")


def test_detail_routes_return_404_for_unknown_ids() -> None:
    response = client.get("/players/999999999")
    assert response.status_code == 404

    response = client.get("/teams/999999999")
    assert response.status_code == 404

    response = client.get("/games/999999999")
    assert response.status_code == 404