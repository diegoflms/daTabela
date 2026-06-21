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


def two_player_names() -> list[str]:
    column = player_display_column()

    if column is None:
        return []

    where_sql = f'WHERE "{column}" IS NOT NULL' if column != "id" else ""
    sql = f'SELECT CAST("{column}" AS TEXT) AS display_name FROM players {where_sql} ORDER BY id LIMIT 2'

    with engine.connect() as connection:
        rows = connection.execute(text(sql)).mappings().all()

    return [str(row["display_name"]) for row in rows if row["display_name"]]


def ask(question: str) -> None:
    response = client.post("/ask", json={"question": question})
    print(f"{response.status_code} POST /ask -> {question}")

    data = response.json()
    print(f"  status: {data.get('status')}")
    print(f"  intent: {data.get('interpreted_as', {}).get('intent')}")
    print(f"  title: {data.get('title')}")
    print(f"  source_tables: {data.get('source_tables')}")
    print(f"  columns: {len(data.get('columns', []))}")
    print(f"  rows: {len(data.get('rows', []))}")

    if response.status_code >= 400:
        print(response.text)


def main() -> None:
    print(client.get("/ask/examples").json())
    print(client.get("/ask/intents").json())

    names = two_player_names()

    if names:
        ask(f"{names[0]} ultimos 5 jogos")
        ask(f"top 3 jogos com mais pontos do {names[0]}")
    else:
        print("Nenhum jogador encontrado para smoke test de /ask.")

    if len(names) >= 2:
        ask(f"{names[0]} vs {names[1]} ultimos 5 jogos")

    ask("top 10 pontos")
    ask("top 10 rebotes")
    ask("top 10 times com mais vitorias na historia")
    ask("lucas ultimos 5 jogos")


if __name__ == "__main__":
    main()