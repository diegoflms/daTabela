from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
REPOSITORY_ROOT = BACKEND_ROOT.parent
DATA_ROOT = REPOSITORY_ROOT / "data"


def run_step(label: str, command: list[str], *, cwd: Path) -> None:
    printable = " ".join(command)

    print("")
    print("=" * 72)
    print(f"[RUN] {label}")
    print(f"CWD: {cwd}")
    print(printable)
    print("=" * 72)

    result = subprocess.run(command, cwd=cwd)

    if result.returncode != 0:
        raise SystemExit(result.returncode)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Roda atualização do /data e depois reimporta/valida o backend."
    )

    parser.add_argument(
        "--skip-data",
        action="store_true",
        help="Não roda update_daily.bat nem build_all_derived.bat. Só atualiza o backend.",
    )
    parser.add_argument(
        "--skip-update-daily",
        action="store_true",
        help="Não roda update_daily.bat.",
    )
    parser.add_argument(
        "--skip-build-derived",
        action="store_true",
        help="Não roda build_all_derived.bat.",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Não roda pytest na etapa de backend.",
    )
    parser.add_argument(
        "--skip-smoke-ask",
        action="store_true",
        help="Não roda scripts.smoke_ask na etapa de backend.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not DATA_ROOT.exists():
        print(f"Pasta data não encontrada: {DATA_ROOT}")
        raise SystemExit(1)

    if not args.skip_data:
        if not args.skip_update_daily:
            update_daily = DATA_ROOT / "update_daily.bat"

            if update_daily.exists():
                run_step("Atualizar dados brutos no /data", ["cmd", "/c", "update_daily.bat"], cwd=DATA_ROOT)
            else:
                print("Aviso: update_daily.bat não encontrado. Pulando.")

        if not args.skip_build_derived:
            build_all = DATA_ROOT / "build_all_derived.bat"

            if build_all.exists():
                run_step("Gerar tabelas derivadas no /data", ["cmd", "/c", "build_all_derived.bat"], cwd=DATA_ROOT)
            else:
                print("Aviso: build_all_derived.bat não encontrado. Pulando.")

    backend_command = [sys.executable, "-m", "scripts.pipeline.refresh_backend"]

    if args.skip_tests:
        backend_command.append("--skip-tests")

    if args.skip_smoke_ask:
        backend_command.append("--skip-smoke-ask")

    run_step("Reimportar e validar backend", backend_command, cwd=BACKEND_ROOT)

    print("")
    print("Atualização data -> backend concluída.")


if __name__ == "__main__":
    main()