import argparse
import sys

from app.config import get_settings
from app.database import engine
from app.importer import import_all_csvs

settings = get_settings()


def main() -> None:
    parser = argparse.ArgumentParser(description="Importa os CSVs finais do DaTabela para SQLite.")
    parser.add_argument("--no-reset-schema", action="store_true", help="Não recria o schema antes da importação.")
    parser.add_argument("--batch-size", type=int, default=1000, help="Tamanho dos lotes de insert.")
    args = parser.parse_args()

    settings.database_dir.mkdir(parents=True, exist_ok=True)

    print("Importação CSV -> SQLite")
    print(f"Banco: {settings.database_path}")
    print(f"Diretório de dados: {settings.data_dir}")
    print("")

    results = import_all_csvs(
        engine=engine,
        data_dir=settings.data_dir,
        reset_schema=not args.no_reset_schema,
        batch_size=args.batch_size,
    )

    imported = 0
    missing = 0
    errors = 0
    total_rows = 0

    for result in results:
        if result.status == "imported":
            imported += 1
            total_rows += result.rows_imported
            print(f"[OK] {result.table_name}: {result.rows_imported} linha(s), {result.columns} coluna(s)")
        elif result.status == "missing_csv":
            missing += 1
            print(f"[AVISO] {result.table_name}: {result.error}")
        else:
            errors += 1
            print(f"[ERRO] {result.table_name}: {result.error}")

    print("")
    print(f"Tabelas importadas: {imported}")
    print(f"CSVs ausentes: {missing}")
    print(f"Erros: {errors}")
    print(f"Linhas totais importadas: {total_rows}")

    if errors:
        raise SystemExit(1)

    if missing:
        print("")
        print("Importação concluída com avisos. Gere os CSVs ausentes em DaTabela/data e rode novamente.")
    else:
        print("")
        print("Importação concluída com sucesso.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nImportação interrompida pelo usuário.")
        sys.exit(130)