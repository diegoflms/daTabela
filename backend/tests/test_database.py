from fastapi.testclient import TestClient

from app.database import check_database_connection
from app.main import app

client = TestClient(app)


def test_database_connection_returns_true() -> None:
    assert check_database_connection() is True


def test_database_health_endpoint_returns_ok() -> None:
    response = client.get("/health/db")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "sqlite"
    assert data["database_path"].endswith("databela.sqlite3")