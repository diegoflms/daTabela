from __future__ import annotations

import argparse
import shutil
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]

FILE_PATTERNS = [
    "setup_backend_parte*.ps1",
    "corrigir_backend_parte*.ps1",
    "refazer_readme_backend*.ps1",
]

DIR_NAMES = [
    "__pycache__",
    ".pytest_cache",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remove arquivos temporários descartáveis do backend."
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Só mostra o que seria removido.",
    )
    parser.add_argument(
        "--with-cache",
        action="store_true",
        help="Também remove __pycache__ e .pytest_cache.",
    )

    return parser.parse_args()


def remove_file(path: Path, *, dry_run: bool) -> None:
    if dry_run:
        print(f"[DRY] remover arquivo: {path.relative_to(BACKEND_ROOT)}")
        return

    path.unlink(missing_ok=True)
    print(f"[OK] removido arquivo: {path.relative_to(BACKEND_ROOT)}")


def remove_dir(path: Path, *, dry_run: bool) -> None:
    if dry_run:
        print(f"[DRY] remover pasta: {path.relative_to(BACKEND_ROOT)}")
        return

    shutil.rmtree(path, ignore_errors=True)
    print(f"[OK] removida pasta: {path.relative_to(BACKEND_ROOT)}")


def main() -> None:
    args = parse_args()

    for pattern in FILE_PATTERNS:
        for path in BACKEND_ROOT.glob(pattern):
            if path.is_file():
                remove_file(path, dry_run=args.dry_run)

    if args.with_cache:
        for dir_name in DIR_NAMES:
            for path in BACKEND_ROOT.rglob(dir_name):
                if path.is_dir():
                    remove_dir(path, dry_run=args.dry_run)

    print("Limpeza concluída.")


if __name__ == "__main__":
    main()