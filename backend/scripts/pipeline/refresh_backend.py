from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
LOGS_DIR = BACKEND_ROOT / "logs"
LAST_LOG = LOGS_DIR / "last_refresh_backend.log"


def write_log_line(message: str) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    with LAST_LOG.open("a", encoding="utf-8") as file:
        file.write(message + "\n")


def run_step(label: str, command: list[str], *, cwd: Path = BACKEND_ROOT) -> None:
    printable = " ".join(command)

    print("")
    print("=" * 72)
    print(f"[RUN] {label}")
    print(printable)
    print("=" * 72)

    write_log_line("")
    write_log_line("=" * 72)
    write_log_line(f"[RUN] {label}")
    write_log_line(printable)
    write_log_line("=" * 72)

    result = subprocess.run(command, cwd=cwd)

    if result.returncode != 0:
        write_log_line(f"[FAIL] {label} retornou codigo {result.returncode}")
        raise SystemExit(result.returncode)

    write_log_line(f"[OK] {label}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Atualiza e valida o backend DaTabela a partir dos CSVs finais já gerados pelo /data."
    )

    parser.add_argument(
        "--skip-import",
        action="store_true",
        help="Não roda scripts.import_csvs. Útil quando só mudou código do backend.",
    )
    parser.add_argument(
        "--skip-validate",
        action="store_true",
        help="Não roda scripts.validate_backend.",
    )
    parser.add_argument(
        "--skip-smoke-all",
        action="store_true",
        help="Não roda scripts.smoke_all.",
    )
    parser.add_argument(
        "--skip-smoke-ask",
        action="store_true",
        help="Não roda scripts.smoke_ask.",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Não roda pytest.",
    )
    parser.add_argument(
        "--only-checks",
        action="store_true",
        help="Atalho para validar sem reimportar dados.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.only_checks:
        args.skip_import = True

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    LAST_LOG.write_text("", encoding="utf-8")

    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    write_log_line(f"DaTabela backend refresh started at {started_at}")
    print(f"DaTabela backend refresh started at {started_at}")

    steps: list[tuple[str, list[str]]] = []

    if not args.skip_import:
        steps.append(("Importar CSVs finais para SQLite", [sys.executable, "-m", "scripts.import_csvs"]))

    if not args.skip_validate:
        steps.append(("Validar tabelas e dados principais", [sys.executable, "-m", "scripts.validate_backend"]))

    if not args.skip_smoke_all:
        steps.append(("Smoke test geral da API", [sys.executable, "-m", "scripts.smoke_all"]))

    if not args.skip_smoke_ask:
        steps.append(("Smoke test do /ask", [sys.executable, "-m", "scripts.smoke_ask"]))

    if not args.skip_tests:
        steps.append(("Rodar pytest", ["pytest"]))

    for label, command in steps:
        run_step(label, command)

    finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    write_log_line(f"DaTabela backend refresh finished at {finished_at}")
    print("")
    print("Tudo certo.")
    print(f"Log: {LAST_LOG}")


if __name__ == "__main__":
    main()