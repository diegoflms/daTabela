from app.config import get_settings
from app.database import engine
from app.importer import get_table_counts

settings = get_settings()


def main() -> None:
    counts = get_table_counts(engine)

    print("Contagem de linhas no SQLite")
    print(f"Banco: {settings.database_path}")
    print("")

    for table_name, count in counts.items():
        if count >= 0:
            print(f"{table_name}: {count}")
        else:
            print(f"{table_name}: tabela ausente")


if __name__ == "__main__":
    main()