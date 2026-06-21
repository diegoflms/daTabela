import argparse

from app.config import get_settings
from app.database import engine
from app.schema import create_schema_from_csv_headers

settings = get_settings()


def main() -> None:
    parser = argparse.ArgumentParser(description="Cria o schema SQLite do DaTabela a partir dos cabeçalhos dos CSVs finais.")
    parser.add_argument("--drop", action="store_true", help="Apaga tabelas existentes antes de recriar o schema.")
    args = parser.parse_args()

    settings.database_dir.mkdir(parents=True, exist_ok=True)

    summary = create_schema_from_csv_headers(
        engine=engine,
        data_dir=settings.data_dir,
        drop_existing=args.drop,
    )

    print("Schema SQLite processado.")
    print(f"Banco: {settings.database_path}")
    print(f"Diretório de dados: {settings.data_dir}")
    print("")

    created = 0
    missing = 0

    for table_name, info in summary.items():
        status = info["status"]
        columns = info["columns"]
        indexes = info["indexes"]

        if status == "created":
            created += 1
            print(f"[OK] {table_name}: {len(columns)} colunas, {indexes} índice(s)")
        else:
            missing += 1
            print(f"[AVISO] {table_name}: CSV não encontrado em {info['csv_path']}")

    print("")
    print(f"Tabelas criadas: {created}")
    print(f"CSVs ausentes: {missing}")

    if missing:
        print("")
        print("Algumas tabelas não foram criadas porque o CSV correspondente não existe.")
        print("Gere as derivadas em DaTabela/data antes de importar tudo.")


if __name__ == "__main__":
    main()