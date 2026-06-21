from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database import engine
from app.main import app

client = TestClient(app)


def first_id(table_name: str) -> int | None:
    with engine.connect() as connection:
        result = connection.execute(
            text(f'SELECT id FROM "{table_name}" ORDER BY id LIMIT 1')
        ).first()

    if result is None:
        return None

    return int(result[0])


def check(path: str) -> None:
    response = client.get(path)
    print(f"{response.status_code} {path}")

    if response.status_code >= 400:
        print(response.text)


def main() -> None:
    player_id = first_id("players")
    team_id = first_id("teams")
    game_id = first_id("games")

    check("/players")
    check("/teams")
    check("/games")

    if player_id is not None:
        check(f"/players/{player_id}")
        check(f"/players/{player_id}/seasons")
        check(f"/players/{player_id}/games")

    if team_id is not None:
        check(f"/teams/{team_id}")
        check(f"/teams/{team_id}/seasons")
        check(f"/teams/{team_id}/games")

    if game_id is not None:
        check(f"/games/{game_id}")
        check(f"/games/{game_id}/player-stats")
        check(f"/games/{game_id}/team-stats")


if __name__ == "__main__":
    main()