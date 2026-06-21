import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.helpers import assert_paginated_endpoint

client = TestClient(app)


@pytest.mark.smoke
def test_openapi_schema_is_available() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200

    data = response.json()
    assert data["info"]["title"] == "DaTabela API"
    assert "paths" in data


@pytest.mark.contract
def test_root_contract() -> None:
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "DaTabela API"
    assert data["docs"] == "/docs"
    assert data["health"] == "/health"


@pytest.mark.contract
@pytest.mark.parametrize(
    "path",
    [
        "/seasons",
        "/teams",
        "/players",
        "/games",
        "/standings",
        "/search/players?q=a",
        "/search/teams?q=a",
        "/search/games?q=a",
    ],
)
def test_paginated_endpoints_contract(path: str) -> None:
    assert_paginated_endpoint(client, path)


@pytest.mark.contract
def test_global_search_contract() -> None:
    response = client.get("/search?q=a&limit=3")

    assert response.status_code == 200

    data = response.json()
    assert data["query"] == "a"
    assert data["limit_per_group"] == 3
    assert "players" in data
    assert "teams" in data
    assert "games" in data
    assert "seasons" in data


@pytest.mark.contract
def test_ranking_metrics_contract() -> None:
    response = client.get("/rankings/players/metrics")

    assert response.status_code == 200

    data = response.json()
    assert data["table"] == "player_seasons"
    assert isinstance(data["metrics"], list)

    response = client.get("/rankings/teams/metrics")

    assert response.status_code == 200

    data = response.json()
    assert data["table"] == "team_seasons"
    assert isinstance(data["metrics"], list)