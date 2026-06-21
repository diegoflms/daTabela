from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_data_health_endpoint_exists() -> None:
    response = client.get("/health/data")

    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "tables" in data
    assert "missing_tables" in data