import argparse
from pathlib import Path

from src.scraping.players_scraper import run_scrape_players


def main() -> None:
	parser = argparse.ArgumentParser(
		description="Scraping de players e player_aliases da LNB."
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
		help="Limita quantidade de temporadas para teste.",
	)

	parser.add_argument(
		"--force",
		action="store_true",
		help="Baixa HTML de novo mesmo se já existir em dados/raw.",
	)

	parser.add_argument(
		"--collect-only",
		action="store_true",
		help="Só coleta URLs dos jogadores, sem baixar páginas individuais.",
	)

	args = parser.parse_args()

	run_scrape_players(
		data_dir=Path(args.data_dir),
		workers=args.workers,
		limit=args.limit,
		force=args.force,
		collect_only=args.collect_only,
	)


if __name__ == "__main__":
	main()