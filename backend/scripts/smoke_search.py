from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def check(path: str) -> None:
    response = client.get(path)
    print(f"{response.status_code} {path}")

    if response.status_code >= 400:
        print(response.text)
        return

    data = response.json()

    if "players" in data:
        print(f"  players: {data['players']['total']}")
        print(f"  teams: {data['teams']['total']}")
        print(f"  games: {data['games']['total']}")
        print(f"  seasons: {data['seasons']['total']}")
    else:
        print(f"  total: {data.get('total')}")


def main() -> None:
    check("/search?q=franca")
    check("/search?q=paulistano&limit=5")
    check("/search/players?q=silva&limit=5")
    check("/search/teams?q=franca&limit=5")
    check("/search/games?q=final&limit=5")


if __name__ == "__main__":
    main()