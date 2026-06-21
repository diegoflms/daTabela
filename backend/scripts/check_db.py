from sqlalchemy import text

from app.config import get_settings
from app.database import engine

settings = get_settings()


def main() -> None:
    settings.database_dir.mkdir(parents=True, exist_ok=True)

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1")).scalar_one()

    print("Conexão com SQLite OK.")
    print(f"Resultado do teste: {result}")
    print(f"Arquivo do banco: {settings.database_path}")


if __name__ == "__main__":
    main()