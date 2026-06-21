import argparse
import subprocess
import sys
from datetime import datetime


def run_module(module: str, *args: str, required: bool = True) -> bool:
    command = [sys.executable, "-m", module, *args]

    print("\n" + "=" * 80)
    print("Executando:", " ".join(command))
    print("=" * 80)

    result = subprocess.run(command)

    if result.returncode != 0:
        print(f"Comando falhou: {' '.join(command)}")

        if required:
            raise SystemExit(result.returncode)

        return False

    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AtualizaÃ§Ã£o diÃ¡ria da base NBBMuse."
    )

    parser.add_argument(
        "--workers",
        default="2",
        help="Quantidade de workers para scraping de boxscores/jogadores.",
    )

    parser.add_argument(
        "--with-players",
        action="store_true",
        help="TambÃ©m atualiza players/player_aliases. Use semanalmente ou no comeÃ§o da temporada.",
    )

    parser.add_argument(
        "--render-failed",
        action="store_true",
        help="Tenta renderizar boxscores falhos com Playwright.",
    )

    args = parser.parse_args()

    started_at = datetime.now()

    print("AtualizaÃ§Ã£o diÃ¡ria NBBMuse")
    print(f"InÃ­cio: {started_at.isoformat(timespec='seconds')}")

    run_module("scripts.scraping.scrape_games")

    if args.with_players:
        run_module("scripts.scraping.scrape_players", "--workers", args.workers)

    run_module("scripts.scraping.scrape_boxscores", "--workers", args.workers)
    run_module("scripts.scraping.scrape_boxscores", "--only-failed", "--workers", args.workers, required=False)

    if args.render_failed:
        run_module("scripts.maintenance.boxscores.render_failed_boxscores", "--wait-ms", "35000", required=False)
        run_module(
            "scripts.scraping.scrape_boxscores",
            "--only-failed",
            "--cache-only",
            "--workers",
            args.workers,
            required=False,
        )

    run_module("scripts.maintenance.boxscores.cleanup_team_only_boxscores", required=False)
    run_module("scripts.maintenance.boxscores.cleanup_dnp_player_game_stats", required=False)

    run_module("scripts.pipeline.build_all_derived")

    run_module("scripts.diagnostics.diagnose_boxscores", required=False)
    run_module("scripts.diagnostics.diagnose_standings", required=False)
    run_module("scripts.diagnostics.diagnose_player_team_seasons", required=False)

    finished_at = datetime.now()

    print("\n" + "=" * 80)
    print("AtualizaÃ§Ã£o diÃ¡ria finalizada.")
    print(f"Fim: {finished_at.isoformat(timespec='seconds')}")
    print(f"DuraÃ§Ã£o: {finished_at - started_at}")
    print("=" * 80)


if __name__ == "__main__":
    main()
