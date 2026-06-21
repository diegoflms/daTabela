import csv
from pathlib import Path


DATA_DIR = Path("dados")
OUT_PATH = DATA_DIR / "diagnostics" / "boxscore_unknowns.csv"


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

	pgs_count = {}

	for row in pgs:
		game_id = row.get("game_id", "")
		if game_id:
			pgs_count[game_id] = pgs_count.get(game_id, 0) + 1

	tgs_count = {}

	for row in tgs:
		game_id = row.get("game_id", "")
		if game_id:
			tgs_count[game_id] = tgs_count.get(game_id, 0) + 1

	failed_ids = {row.get("game_id", "") for row in failed}

	rows = []

	for game in games:
		game_id = game.get("id", "")

		if not game.get("boxscore_url"):
			continue

		if game_id in failed_ids:
			continue

		player_rows = pgs_count.get(game_id, 0)
		team_rows = tgs_count.get(game_id, 0)

		if player_rows > 0 and team_rows == 2:
			continue

		rows.append(
			{
				"game_id": game_id,
				"season_id": game.get("season_id", ""),
				"game_date": game.get("game_date", ""),
				"home_team_name_raw": game.get("home_team_name_raw", ""),
				"away_team_name_raw": game.get("away_team_name_raw", ""),
				"home_score": game.get("home_score", ""),
				"away_score": game.get("away_score", ""),
				"player_game_stats_rows": player_rows,
				"team_game_stats_rows": team_rows,
				"boxscore_url": game.get("boxscore_url", ""),
				"local_html": f"dados/raw/boxscores/game_{game_id}.html",
			}
		)

	fieldnames = [
		"game_id",
		"season_id",
		"game_date",
		"home_team_name_raw",
		"away_team_name_raw",
		"home_score",
		"away_score",
		"player_game_stats_rows",
		"team_game_stats_rows",
		"boxscore_url",
		"local_html",
	]

	write_csv(OUT_PATH, rows, fieldnames)

	print(f"Arquivo gerado em: {OUT_PATH}")
	print(f"Inconsistências: {len(rows)}")

	for row in rows:
		print(
			row["game_id"],
			row["season_id"],
			row["home_team_name_raw"],
			"x",
			row["away_team_name_raw"],
			"PGS:",
			row["player_game_stats_rows"],
			"TGS:",
			row["team_game_stats_rows"],
		)


if __name__ == "__main__":
	main()
