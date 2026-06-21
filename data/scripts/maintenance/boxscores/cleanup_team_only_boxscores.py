import csv
from collections import Counter
from datetime import datetime
from pathlib import Path


DATA_DIR = Path("dados")
OUT_PATH = DATA_DIR / "diagnostics" / "removed_team_only_boxscores.csv"


FAILED_FIELDS = [
	"id",
	"game_id",
	"season_id",
	"boxscore_url",
	"error_type",
	"error_message",
	"last_attempt_at",
]


def read_csv(path: Path) -> tuple[list[dict], list[str]]:
	if not path.exists():
		return [], []

	with path.open("r", encoding="utf-8-sig", newline="") as file:
		reader = csv.DictReader(file)
		return list(reader), reader.fieldnames or []


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)

	with path.open("w", encoding="utf-8", newline="") as file:
		writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
		writer.writeheader()
		writer.writerows(rows)


def next_id(rows: list[dict]) -> int:
	ids = []

	for row in rows:
		try:
			ids.append(int(row.get("id", 0)))
		except ValueError:
			pass

	return max(ids, default=0) + 1


def now() -> str:
	return datetime.now().isoformat(timespec="seconds")


def main() -> None:
	games, _ = read_csv(DATA_DIR / "games.csv")
	pgs, _ = read_csv(DATA_DIR / "player_game_stats.csv")
	tgs, tgs_fields = read_csv(DATA_DIR / "team_game_stats.csv")
	failed, failed_fields = read_csv(DATA_DIR / "_runtime" / "failed_boxscores.csv")

	if not failed_fields:
		failed_fields = FAILED_FIELDS

	games_by_id = {
		row.get("id", ""): row
		for row in games
		if row.get("id")
	}

	pgs_count = Counter(
		row.get("game_id", "")
		for row in pgs
		if row.get("game_id")
	)

	tgs_count = Counter(
		row.get("game_id", "")
		for row in tgs
		if row.get("game_id")
	)

	# Caso contaminado: tem team_game_stats, mas não tem player_game_stats.
	bad_game_ids = sorted(
		game_id
		for game_id, count in tgs_count.items()
		if count > 0 and pgs_count.get(game_id, 0) == 0
	)

	if not bad_game_ids:
		print("Nenhum boxscore team-only encontrado.")
		return

	bad_set = set(bad_game_ids)

	removed_rows = [
		row for row in tgs
		if row.get("game_id", "") in bad_set
	]

	kept_tgs = [
		row for row in tgs
		if row.get("game_id", "") not in bad_set
	]

	failed_by_game = {
		row.get("game_id", ""): row
		for row in failed
		if row.get("game_id")
	}

	next_failed_id = next_id(failed)

	for game_id in bad_game_ids:
		game = games_by_id.get(game_id, {})

		new_failed = {
			"id": "",
			"game_id": game_id,
			"season_id": game.get("season_id", ""),
			"boxscore_url": game.get("boxscore_url", ""),
			"error_type": "empty_boxscore_template",
			"error_message": (
				"Boxscore tinha linhas de time, mas nenhuma linha útil de jogador. "
				"Linhas removidas de team_game_stats."
			),
			"last_attempt_at": now(),
		}

		if game_id in failed_by_game:
			failed_by_game[game_id].update(
				{key: value for key, value in new_failed.items() if key != "id"}
			)
		else:
			new_failed["id"] = next_failed_id
			failed.append(new_failed)
			failed_by_game[game_id] = new_failed
			next_failed_id += 1

	report_rows = []

	for game_id in bad_game_ids:
		game = games_by_id.get(game_id, {})

		report_rows.append(
			{
				"game_id": game_id,
				"season_id": game.get("season_id", ""),
				"home_team_name_raw": game.get("home_team_name_raw", ""),
				"away_team_name_raw": game.get("away_team_name_raw", ""),
				"team_game_stats_rows_removed": tgs_count.get(game_id, 0),
				"player_game_stats_rows": pgs_count.get(game_id, 0),
				"boxscore_url": game.get("boxscore_url", ""),
			}
		)

	write_csv(DATA_DIR / "team_game_stats.csv", kept_tgs, tgs_fields)

	write_csv(
		DATA_DIR / "_runtime" / "failed_boxscores.csv",
		sorted(failed, key=lambda row: int(row.get("id", 0))),
		failed_fields,
	)

	write_csv(
		OUT_PATH,
		report_rows,
		[
			"game_id",
			"season_id",
			"home_team_name_raw",
			"away_team_name_raw",
			"team_game_stats_rows_removed",
			"player_game_stats_rows",
			"boxscore_url",
		],
	)

	print(f"Jogos team-only removidos: {len(bad_game_ids)}")
	print(f"Linhas removidas de team_game_stats: {len(removed_rows)}")
	print(f"Relatório: {OUT_PATH}")

	for row in report_rows:
		print(
			row["game_id"],
			row["season_id"],
			row["home_team_name_raw"],
			"x",
			row["away_team_name_raw"],
			"removidas:",
			row["team_game_stats_rows_removed"],
		)


if __name__ == "__main__":
	main()
