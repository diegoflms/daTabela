from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def assert_paginated_response(path: str) -> None:
    response = client.get(path)

    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert isinstance(data["items"], list)


def test_list_seasons_endpoint() -> None:
    assert_paginated_response("/seasons")


def test_list_teams_endpoint() -> None:
    assert_paginated_response("/teams")


def test_list_players_endpoint() -> None:
    assert_paginated_response("/players")


def test_list_games_endpoint() -> None:
    assert_paginated_response("/games")


def test_list_players_accepts_search_query() -> None:
    assert_paginated_response("/players?q=lucas")


def test_list_teams_accepts_search_query() -> None:
    assert_paginated_response("/teams?q=franca")


def test_list_games_accepts_filters() -> None:
    assert_paginated_response("/games?season_id=1&limit=10&offset=0")