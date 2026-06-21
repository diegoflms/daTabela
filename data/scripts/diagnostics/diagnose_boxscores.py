import csv
from collections import Counter, defaultdict
from pathlib import Path


DATA_DIR = Path("dados")
DIAG_DIR = DATA_DIR / "diagnostics"


def read_csv(path: Path) -> list[dict]:
	if not path.exists():
		return []

	with path.open("r", encoding="utf-8-sig", newline="") as file:
		return list(csv.DictReader(file))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)

	with path.open("w", encoding="utf-8", newline="") as file:
		writer = csv.DictWriter(file, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(rows)


def main() -> None:
	games = read_csv(DATA_DIR / "games.csv")
	pgs = read_csv(DATA_DIR / "player_game_stats.csv")
	tgs = read_csv(DATA_DIR / "team_game_stats.csv")
	failed = read_csv(DATA_DIR / "_runtime" / "failed_boxscores.csv")
	unresolved = read_csv(DATA_DIR / "_runtime" / "unresolved_boxscore_players.csv")

	print("\n=== RESUMO ===")
	print(f"Jogos em games.csv: {len(games)}")
	print(f"Player game stats: {len(pgs)}")
	print(f"Team game stats: {len(tgs)}")
	print(f"Boxscores com falha: {len(failed)}")
	print(f"Jogadores não resolvidos: {len(unresolved)}")

	print("\n=== FALHAS POR TIPO ===")
	failed_by_type = Counter(row.get("error_type", "") for row in failed)
	for error_type, count in failed_by_type.most_common():
		print(f"{error_type}: {count}")

	write_csv(
		DIAG_DIR / "failed_boxscores_by_type.csv",
		[
			{"error_type": error_type, "count": count}
			for error_type, count in failed_by_type.most_common()
		],
		["error_type", "count"],
	)

	print("\n=== JOGADORES NÃO RESOLVIDOS POR MOTIVO ===")
	unresolved_by_reason = Counter(row.get("reason", "") for row in unresolved)
	for reason, count in unresolved_by_reason.most_common():
		print(f"{reason}: {count}")

	write_csv(
		DIAG_DIR / "unresolved_players_by_reason.csv",
		[
			{"reason": reason, "count": count}
			for reason, count in unresolved_by_reason.most_common()
		],
		["reason", "count"],
	)

	pgs_games = {row.get("game_id", "") for row in pgs}
	tgs_by_game = defaultdict(int)

	for row in tgs:
		tgs_by_game[row.get("game_id", "")] += 1

	missing_team_stats = []

	for game_id in sorted(pgs_games, key=lambda x: int(x) if x.isdigit() else 0):
		count = tgs_by_game.get(game_id, 0)

		if count != 2:
			matching_game = next((g for g in games if g.get("id") == game_id), {})

			missing_team_stats.append(
				{
					"game_id": game_id,
					"team_stats_rows": count,
					"season_id": matching_game.get("season_id", ""),
					"home_team_id": matching_game.get("home_team_id", ""),
					"away_team_id": matching_game.get("away_team_id", ""),
					"boxscore_url": matching_game.get("boxscore_url", ""),
				}
			)

	print("\n=== JOGOS COM TEAM_GAME_STATS INCOMPLETO ===")
	print(f"Jogos com != 2 linhas de time: {len(missing_team_stats)}")

	write_csv(
		DIAG_DIR / "missing_team_stats_games.csv",
		missing_team_stats,
		[
			"game_id",
			"team_stats_rows",
			"season_id",
			"home_team_id",
			"away_team_id",
			"boxscore_url",
		],
	)

	write_csv(
		DIAG_DIR / "failed_boxscores_sample.csv",
		failed[:100],
		failed[0].keys() if failed else ["id"],
	)

	write_csv(
		DIAG_DIR / "unresolved_boxscore_players_sample.csv",
		unresolved[:200],
		unresolved[0].keys() if unresolved else ["id"],
	)

	print("\nArquivos gerados em:")
	print(DIAG_DIR)


if __name__ == "__main__":
	main()
