from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def check(path: str) -> dict:
    response = client.get(path)
    print(f"{response.status_code} {path}")

    if response.status_code >= 400:
        print(response.text)

    return response.json()


def main() -> None:
    check("/standings")

    player_metrics = check("/rankings/players/metrics")
    team_metrics = check("/rankings/teams/metrics")

    if player_metrics.get("metrics"):
        first_metric = player_metrics["metrics"][0]["key"]
        check(f"/rankings/players/{first_metric}?limit=10&min_games=1")
    else:
        print("Nenhuma métrica de jogador disponível em player_seasons.")

    if team_metrics.get("metrics"):
        first_metric = team_metrics["metrics"][0]["key"]
        check(f"/rankings/teams/{first_metric}?limit=10")
    else:
        print("Nenhuma métrica de time disponível em team_seasons.")


if __name__ == "__main__":
    main()