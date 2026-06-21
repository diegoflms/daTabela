import csv
from datetime import datetime
from pathlib import Path

from src.scraping.boxscores_scraper import (
	PLAYER_GAME_STATS_FIELDS,
	UNRESOLVED_PLAYERS_FIELDS,
	PlayerResolver,
)
from src.utils.text import clean_text


DATA_DIR = Path("dados")
REPORT_PATH = DATA_DIR / "diagnostics" / "removed_dnp_player_game_stats.csv"


STAT_FIELDS = [
	"points",
	"fg_made",
	"fg_attempted",
	"three_made",
	"three_attempted",
	"two_made",
	"two_attempted",
	"ft_made",
	"ft_attempted",
	"offensive_rebounds",
	"defensive_rebounds",
	"total_rebounds",
	"assists",
	"steals",
	"blocks",
	"fouls_committed",
	"fouls_received",
	"turnovers",
	"dunks",
	"plus_minus",
	"efficiency",
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


def now() -> str:
	return datetime.now().isoformat(timespec="seconds")


def as_float(value: str) -> float:
	value = clean_text(value).replace(",", ".")

	if not value:
		return 0.0

	try:
		return float(value)
	except ValueError:
		return 0.0


def is_dnp(row: dict) -> bool:
	minutes = as_float(row.get("minutes_decimal", ""))

	has_any_stat = any(
		as_float(row.get(field, "")) != 0
		for field in STAT_FIELDS
	)

	return minutes <= 0 and not has_any_stat


def team_side_for_row(row: dict, games_by_id: dict[str, dict]) -> str:
	game = games_by_id.get(clean_text(row.get("game_id")), {})
	team_id = clean_text(row.get("team_id"))

	if team_id == clean_text(game.get("home_team_id")):
		return "home"

	if team_id == clean_text(game.get("away_team_id")):
		return "away"

	return ""


def rebuild_unresolved(
	pgs: list[dict],
	players: list[dict],
	aliases: list[dict],
	team_aliases: list[dict],
	games: list[dict],
) -> list[dict]:
	resolver = PlayerResolver(
		players_rows=players,
		player_aliases_rows=aliases,
		team_aliases_rows=team_aliases,
	)

	games_by_id = {
		clean_text(row.get("id")): row
		for row in games
		if clean_text(row.get("id"))
	}

	unresolved = []
	next_id = 1

	for row in pgs:
		if clean_text(row.get("player_id")):
			continue

		player_id, candidates, reason = resolver.resolve(
			season_id=clean_text(row.get("season_id")),
			team_id=clean_text(row.get("team_id")),
			player_name=clean_text(row.get("player_name_raw")),
			jersey_number=clean_text(row.get("jersey_number")),
		)

		if player_id:
			row["player_id"] = player_id
			row["needs_manual_review"] = 0
			continue

		unresolved.append(
			{
				"id": next_id,
				"game_id": clean_text(row.get("game_id")),
				"season_id": clean_text(row.get("season_id")),
				"team_id": clean_text(row.get("team_id")),
				"team_side": team_side_for_row(row, games_by_id),
				"player_name_raw": clean_text(row.get("player_name_raw")),
				"jersey_number": clean_text(row.get("jersey_number")),
				"candidate_player_ids": ",".join(candidates),
				"reason": reason,
				"source_url": clean_text(row.get("source_url")),
				"created_at": now(),
			}
		)

		next_id += 1

	return unresolved


def main() -> None:
	pgs, _ = read_csv(DATA_DIR / "player_game_stats.csv")
	players, _ = read_csv(DATA_DIR / "players.csv")
	aliases, _ = read_csv(DATA_DIR / "player_aliases.csv")
	team_aliases, _ = read_csv(DATA_DIR / "team_aliases.csv")
	games, _ = read_csv(DATA_DIR / "games.csv")

	removed = []
	kept = []

	for row in pgs:
		if is_dnp(row):
			removed.append(row)
		else:
			kept.append(row)

	unresolved = rebuild_unresolved(
		pgs=kept,
		players=players,
		aliases=aliases,
		team_aliases=team_aliases,
		games=games,
	)

	report_fields = PLAYER_GAME_STATS_FIELDS

	write_csv(DATA_DIR / "player_game_stats.csv", kept, PLAYER_GAME_STATS_FIELDS)
	write_csv(DATA_DIR / "_runtime" / "unresolved_boxscore_players.csv", unresolved, UNRESOLVED_PLAYERS_FIELDS)
	write_csv(REPORT_PATH, removed, report_fields)

	print(f"Linhas DNP removidas de player_game_stats: {len(removed)}")
	print(f"Linhas restantes em player_game_stats: {len(kept)}")
	print(f"Jogadores ainda não resolvidos: {len(unresolved)}")
	print(f"Relatório dos removidos: {REPORT_PATH}")


if __name__ == "__main__":
	main()
