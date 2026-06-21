from app.config import get_settings
from app.database import engine
from app.schema import create_schema_from_csv_headers

settings = get_settings()


def main() -> None:
    settings.database_dir.mkdir(parents=True, exist_ok=True)

    summary = create_schema_from_csv_headers(
        engine=engine,
        data_dir=settings.data_dir,
        drop_existing=True,
    )

    created = sum(1 for info in summary.values() if info["status"] == "created")
    missing = sum(1 for info in summary.values() if info["status"] == "missing_csv")

    print("Banco resetado.")
    print(f"Banco: {settings.database_path}")
    print(f"Tabelas criadas: {created}")
    print(f"CSVs ausentes: {missing}")


if __name__ == "__main__":
    main()