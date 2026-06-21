import argparse
from pathlib import Path

from src.scraping.boxscores_scraper import run_scrape_boxscores


def main() -> None:
	parser = argparse.ArgumentParser(
		description="Scraping de player_game_stats e team_game_stats."
	)

	parser.add_argument(
		"--data-dir",
		default="dados",
		help="Pasta onde ficam os CSVs.",
	)

	parser.add_argument(
		"--workers",
		type=int,
		default=2,
		help="Número de threads. Use 1 a 3 para não sobrecarregar o site.",
	)

	parser.add_argument(
		"--limit",
		type=int,
		default=None,
		help="Limita quantidade de jogos para teste.",
	)

	parser.add_argument(
		"--force",
		action="store_true",
		help="Baixa HTML de novo mesmo se já existir em dados/raw/boxscores.",
	)

	parser.add_argument(
		"--strict-players",
		action="store_true",
		help="Interrompe se algum jogador não for resolvido.",
	)

	parser.add_argument(
		"--only-failed",
		action="store_true",
		help="Processa apenas jogos presentes em dados/_runtime/failed_boxscores.csv.",
	)

	parser.add_argument(
		"--cache-only",
		action="store_true",
		help="Não baixa HTML novo; usa apenas dados/raw/boxscores.",
	)

	args = parser.parse_args()

	run_scrape_boxscores(
		data_dir=Path(args.data_dir),
		workers=args.workers,
		limit=args.limit,
		force=args.force,
		strict_players=args.strict_players,
		only_failed=args.only_failed,
		cache_only=args.cache_only,
	)


if __name__ == "__main__":
	main()