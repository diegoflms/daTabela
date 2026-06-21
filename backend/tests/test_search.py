from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_global_search_endpoint() -> None:
    response = client.get("/search?q=franca")

    assert response.status_code == 200

    data = response.json()
    assert data["query"] == "franca"
    assert "players" in data
    assert "teams" in data
    assert "games" in data
    assert "seasons" in data


def test_global_search_requires_query() -> None:
    response = client.get("/search")

    assert response.status_code == 422


def test_search_players_endpoint() -> None:
    response = client.get("/search/players?q=silva")

    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data


def test_search_teams_endpoint() -> None:
    response = client.get("/search/teams?q=franca")

    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data


def test_search_games_endpoint() -> None:
    response = client.get("/search/games?q=final")

    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data