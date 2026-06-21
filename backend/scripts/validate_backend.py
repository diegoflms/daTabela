from app.importer import get_table_counts
from app.database import engine
from app.models.table_specs import FINAL_TABLE_SPECS

CORE_TABLES = [
    "seasons",
    "teams",
    "players",
    "games",
    "player_game_stats",
    "team_game_stats",
]


def main() -> None:
    counts = get_table_counts(engine)

    print("Validação do backend DaTabela")
    print("")

    errors: list[str] = []

    for spec in FINAL_TABLE_SPECS:
        count = counts.get(spec.table_name, -1)

        if count < 0:
            errors.append(f"Tabela ausente: {spec.table_name}")
            print(f"[ERRO] {spec.table_name}: ausente")
        else:
            print(f"[OK] {spec.table_name}: {count} linha(s)")

    print("")

    for table_name in CORE_TABLES:
        count = counts.get(table_name, 0)

        if count <= 0:
            errors.append(f"Tabela principal vazia: {table_name}")

    if errors:
        print("Problemas encontrados:")
        for error in errors:
            print(f"- {error}")

        raise SystemExit(1)

    print("Validação concluída com sucesso.")


if __name__ == "__main__":
    main()