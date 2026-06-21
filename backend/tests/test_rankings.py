import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def assert_paginated_response(path: str) -> dict:
    response = client.get(path)

    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data

    return data


def test_standings_endpoint() -> None:
    assert_paginated_response("/standings")


def test_player_ranking_metrics_endpoint() -> None:
    response = client.get("/rankings/players/metrics")

    assert response.status_code == 200

    data = response.json()
    assert data["table"] == "player_seasons"
    assert "metrics" in data
    assert isinstance(data["metrics"], list)


def test_team_ranking_metrics_endpoint() -> None:
    response = client.get("/rankings/teams/metrics")

    assert response.status_code == 200

    data = response.json()
    assert data["table"] == "team_seasons"
    assert "metrics" in data
    assert isinstance(data["metrics"], list)


def test_first_available_player_ranking() -> None:
    response = client.get("/rankings/players/metrics")
    metrics = response.json()["metrics"]

    if not metrics:
        pytest.skip("Nenhuma métrica disponível em player_seasons.")

    metric = metrics[0]["key"]
    data = assert_paginated_response(f"/rankings/players/{metric}?limit=10&min_games=0")

    assert "metric" in data
    assert data["metric"]["key"] == metric


def test_first_available_team_ranking() -> None:
    response = client.get("/rankings/teams/metrics")
    metrics = response.json()["metrics"]

    if not metrics:
        pytest.skip("Nenhuma métrica disponível em team_seasons.")

    metric = metrics[0]["key"]
    data = assert_paginated_response(f"/rankings/teams/{metric}?limit=10&min_games=0")

    assert "metric" in data
    assert data["metric"]["key"] == metric


def test_unknown_player_ranking_metric_returns_404() -> None:
    response = client.get("/rankings/players/metrica_que_nao_existe")

    assert response.status_code == 404


def test_unknown_team_ranking_metric_returns_404() -> None:
    response = client.get("/rankings/teams/metrica_que_nao_existe")

    assert response.status_code == 404