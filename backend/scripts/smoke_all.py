from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


PATHS = [
    "/",
    "/health",
    "/health/db",
    "/health/schema",
    "/health/data",
    "/seasons?limit=3",
    "/teams?limit=3",
    "/players?limit=3",
    "/games?limit=3",
    "/standings?limit=3",
    "/rankings/players/metrics",
    "/rankings/teams/metrics",
    "/search?q=franca&limit=3",
]


def main() -> None:
    failed = 0

    print("Smoke test geral da API")
    print("")

    for path in PATHS:
        response = client.get(path)
        status = response.status_code
        label = "OK" if status < 400 else "ERRO"

        print(f"[{label}] {status} {path}")

        if status >= 400:
            failed += 1
            print(response.text)

    print("")

    if failed:
        print(f"Smoke test finalizado com {failed} falha(s).")
        raise SystemExit(1)

    print("Smoke test finalizado com sucesso.")


if __name__ == "__main__":
    main()