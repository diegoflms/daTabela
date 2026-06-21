import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.contract
@pytest.mark.parametrize(
    "path",
    [
        "/players?limit=1",
        "/teams?limit=1",
        "/games?limit=1",
        "/standings?limit=1",
    ],
)
def test_limit_one_returns_at_most_one_item(path: str) -> None:
    response = client.get(path)

    assert response.status_code == 200

    data = response.json()
    assert data["limit"] == 1
    assert len(data["items"]) <= 1


@pytest.mark.contract
@pytest.mark.parametrize(
    "path",
    [
        "/players?limit=999",
        "/teams?limit=999",
        "/games?limit=999",
        "/standings?limit=999",
    ],
)
def test_limit_above_max_returns_validation_error(path: str) -> None:
    response = client.get(path)

    assert response.status_code == 422


@pytest.mark.contract
@pytest.mark.parametrize(
    "path",
    [
        "/players?offset=-1",
        "/teams?offset=-1",
        "/games?offset=-1",
        "/standings?offset=-1",
    ],
)
def test_negative_offset_returns_validation_error(path: str) -> None:
    response = client.get(path)

    assert response.status_code == 422


@pytest.mark.contract
@pytest.mark.parametrize(
    "path",
    [
        "/players/999999999",
        "/teams/999999999",
        "/games/999999999",
    ],
)
def test_unknown_detail_ids_return_404(path: str) -> None:
    response = client.get(path)

    assert response.status_code == 404