from fastapi.testclient import TestClient

from app.main import app
from app.models.table_specs import FINAL_TABLE_SPECS
from app.schema import infer_sqlite_type, normalize_column_name

client = TestClient(app)


def test_final_table_specs_have_unique_names() -> None:
    table_names = [spec.table_name for spec in FINAL_TABLE_SPECS]

    assert len(table_names) == len(set(table_names))


def test_final_table_specs_have_expected_core_tables() -> None:
    table_names = {spec.table_name for spec in FINAL_TABLE_SPECS}

    expected = {
        "seasons",
        "teams",
        "players",
        "games",
        "player_game_stats",
        "team_game_stats",
        "standings",
        "player_team_seasons",
        "player_career_totals",
        "player_records",
    }

    assert expected.issubset(table_names)


def test_column_name_normalization() -> None:
    assert normalize_column_name("Player ID") == "player_id"
    assert normalize_column_name(" FG% ") == "fg"


def test_sqlite_type_inference() -> None:
    assert infer_sqlite_type("player_id") == "INTEGER"
    assert infer_sqlite_type("season_id") == "INTEGER"
    assert infer_sqlite_type("points_per_game") == "REAL"
    assert infer_sqlite_type("name") == "TEXT"


def test_schema_health_endpoint() -> None:
    response = client.get("/health/schema")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["tables"] == len(FINAL_TABLE_SPECS)
    assert "players" in data["table_names"]
    assert "games" in data["table_names"]