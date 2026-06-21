import csv
from pathlib import Path


DATA_DIR = Path("dados")
OUT_PATH = DATA_DIR / "diagnostics" / "boxscore_status.csv"


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
	player_stats = read_csv(DATA_DIR / "player_game_stats.csv")
	team_stats = read_csv(DATA_DIR / "team_game_stats.csv")
	failed = read_csv(DATA_DIR / "_runtime" / "failed_boxscores.csv")

	player_games = {row["game_id"] for row in player_stats if row.get("game_id")}

	team_count_by_game = {}

	for row in team_stats:
		game_id = row.get("game_id", "")
		if not game_id:
			continue

		team_count_by_game[game_id] = team_count_by_game.get(game_id, 0) + 1

	failed_by_game = {
		row["game_id"]: row
		for row in failed
		if row.get("game_id")
	}

	rows = []

	for game in games:
		game_id = game.get("id", "")
		boxscore_url = game.get("boxscore_url", "")
		failed_row = failed_by_game.get(game_id)

		has_player_stats = game_id in player_games
		team_rows = team_count_by_game.get(game_id, 0)

		if has_player_stats and team_rows == 2:
			status = "success"
			has_boxscore_stats = 1
			error_type = ""
			error_message = ""
		elif failed_row:
			status = "failed"
			has_boxscore_stats = 0
			error_type = failed_row.get("error_type", "")
			error_message = failed_row.get("error_message", "")
		elif not boxscore_url:
			status = "no_boxscore_url"
			has_boxscore_stats = 0
			error_type = "missing_boxscore_url"
			error_message = ""
		else:
			status = "unknown"
			has_boxscore_stats = 0
			error_type = "not_processed_or_inconsistent"
			error_message = ""

		rows.append(
			{
				"game_id": game_id,
				"season_id": game.get("season_id", ""),
				"competition": game.get("competition", ""),
				"game_date": game.get("game_date", ""),
				"home_team_name_raw": game.get("home_team_name_raw", ""),
				"away_team_name_raw": game.get("away_team_name_raw", ""),
				"home_score": game.get("home_score", ""),
				"away_score": game.get("away_score", ""),
				"boxscore_url": boxscore_url,
				"status": status,
				"has_boxscore_stats": has_boxscore_stats,
				"team_game_stats_rows": team_rows,
				"has_player_game_stats": int(has_player_stats),
				"error_type": error_type,
				"error_message": error_message,
			}
		)

	fieldnames = [
		"game_id",
		"season_id",
		"competition",
		"game_date",
		"home_team_name_raw",
		"away_team_name_raw",
		"home_score",
		"away_score",
		"boxscore_url",
		"status",
		"has_boxscore_stats",
		"team_game_stats_rows",
		"has_player_game_stats",
		"error_type",
		"error_message",
	]

	write_csv(OUT_PATH, rows, fieldnames)

	print(f"Arquivo gerado em: {OUT_PATH}")
	print(f"Total de jogos: {len(rows)}")
	print(f"Sucesso: {sum(1 for row in rows if row['status'] == 'success')}")
	print(f"Falha: {sum(1 for row in rows if row['status'] == 'failed')}")
	print(f"Sem URL: {sum(1 for row in rows if row['status'] == 'no_boxscore_url')}")
	print(f"Inconsistente/desconhecido: {sum(1 for row in rows if row['status'] == 'unknown')}")


if __name__ == "__main__":
	main()
