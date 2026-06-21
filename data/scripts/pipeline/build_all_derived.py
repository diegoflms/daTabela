import subprocess
import sys
from datetime import datetime


COMMANDS = [
    ["scripts.build.create_manual_tables"],
    ["scripts.build.build_standings"],
    ["scripts.build.build_team_seasons"],
    ["scripts.build.build_player_team_seasons"],
    ["scripts.build.build_player_seasons"],
    ["scripts.build.build_player_career_totals"],
    ["scripts.build.build_player_records"],
]


def run_module(module: str, *args: str) -> None:
    command = [sys.executable, "-m", module, *args]

    print("\n" + "=" * 80)
    print("Executando:", " ".join(command))
    print("=" * 80)

    subprocess.run(command, check=True)


def main() -> None:
    started_at = datetime.now()

    print("Pipeline de tabelas derivadas")
    print(f"InÃ­cio: {started_at.isoformat(timespec='seconds')}")

    for command in COMMANDS:
        run_module(*command)

    finished_at = datetime.now()

    print("\n" + "=" * 80)
    print("Derivadas geradas com sucesso.")
    print(f"Fim: {finished_at.isoformat(timespec='seconds')}")
    print(f"DuraÃ§Ã£o: {finished_at - started_at}")
    print("=" * 80)


if __name__ == "__main__":
    main()
