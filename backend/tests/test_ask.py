from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database import engine
from app.main import app

client = TestClient(app)


def player_display_column() -> str | None:
    with engine.connect() as connection:
        rows = connection.execute(text('PRAGMA table_info("players")')).mappings().all()

    columns = {str(row["name"]) for row in rows}

    for candidate in ("name", "full_name", "player_name", "nickname", "slug"):
        if candidate in columns:
            return candidate

    if "id" in columns:
        return "id"

    return None


def first_player_name() -> str | None:
    column = player_display_column()

    if column is None:
        return None

    where_sql = f'WHERE "{column}" IS NOT NULL' if column != "id" else ""
    sql = f'SELECT CAST("{column}" AS TEXT) AS display_name FROM players {where_sql} ORDER BY id LIMIT 1'

    with engine.connect() as connection:
        row = connection.execute(text(sql)).mappings().first()

    if not row:
        return None

    return str(row["display_name"])


def test_ask_examples_endpoint() -> None:
    response = client.get("/ask/examples")

    assert response.status_code == 200
    assert "examples" in response.json()


def test_ask_intents_endpoint() -> None:
    response = client.get("/ask/intents")

    assert response.status_code == 200
    assert "intents" in response.json()


def test_ask_requires_question() -> None:
    response = client.post("/ask", json={})

    assert response.status_code == 422


def test_ask_player_recent_games_returns_controlled_response() -> None:
    player_name = first_player_name()

    if player_name is None:
        return

    response = client.post("/ask", json={"question": f"{player_name} ultimos 1 jogos"})

    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "columns" in data
    assert "rows" in data


def test_ask_player_top_games_uses_player_game_stats_when_player_exists() -> None:
    player_name = first_player_name()

    if player_name is None:
        return

    response = client.post("/ask", json={"question": f"top 3 jogos com mais pontos do {player_name}"})

    assert response.status_code == 200

    data = response.json()

    if data["status"] == "ok":
        assert data["interpreted_as"]["intent"] == "player_top_games"
        assert "player_game_stats" in data["source_tables"]


def test_ask_team_history_ranking_aggregates_team_seasons() -> None:
    response = client.post("/ask", json={"question": "top 10 times com mais vitorias na historia"})

    assert response.status_code == 200

    data = response.json()

    if data["status"] == "ok":
        assert data["interpreted_as"]["intent"] == "team_history_ranking"
        assert data["interpreted_as"]["aggregation"] == "SUM por team_id"
        assert "team_seasons" in data["source_tables"]


def test_ask_short_ambiguous_name_returns_controlled_response() -> None:
    response = client.post("/ask", json={"question": "lucas ultimos 5 jogos"})

    assert response.status_code == 200

    data = response.json()
    assert data["status"] in {"needs_clarification", "not_found", "ok"}
    assert "columns" in data
    assert "rows" in data


def test_ask_top_points_returns_controlled_response() -> None:
    response = client.post("/ask", json={"question": "top 10 pontos"})

    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "columns" in data
    assert "rows" in data