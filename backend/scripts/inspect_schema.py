from sqlalchemy import inspect, text

from app.config import get_settings
from app.database import engine
from app.models.table_specs import FINAL_TABLE_SPECS

settings = get_settings()


def main() -> None:
    inspector = inspect(engine)

    print("Catálogo de tabelas finais do DaTabela")
    print(f"Banco: {settings.database_path}")
    print(f"Dados: {settings.data_dir}")
    print("")

    existing_tables = set(inspector.get_table_names())

    for spec in FINAL_TABLE_SPECS:
        exists = spec.table_name in existing_tables
        status = "OK" if exists else "AUSENTE"

        print(f"[{status}] {spec.table_name}")
        print(f"  CSV: {spec.csv_file}")
        print(f"  Ideia: {spec.description}")

        if exists:
            columns = inspector.get_columns(spec.table_name)
            row_count = engine.connect().execute(text(f'SELECT COUNT(*) FROM "{spec.table_name}"')).scalar_one()
            print(f"  Colunas: {len(columns)}")
            print(f"  Linhas: {row_count}")

        print("")


if __name__ == "__main__":
    main()