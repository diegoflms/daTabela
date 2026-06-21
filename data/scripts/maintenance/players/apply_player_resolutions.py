import argparse
import csv
from datetime import datetime
from pathlib import Path

from src.scraping.boxscores_scraper import (
	PLAYER_GAME_STATS_FIELDS,
	UNRESOLVED_PLAYERS_FIELDS,
	PlayerResolver,
)
from src.utils.text import clean_text, identity_key


DATA_DIR = Path("dados")
SUGGESTIONS_PATH = DATA_DIR / "diagnostics" / "player_resolution_suggestions.csv"


REQUIRED_ALIAS_FIELDS = [
	"id",
	"player_id",
	"alias",
	"alias_type",
	"season_id",
	"team_name_raw",
	"jersey_number",
	"source",
	"created_at",
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


def build_game_map(games: list[dict]) -> dict[str, dict]:
	return {
		clean_text(row.get("id")): row
		for row in games
		if clean_text(row.get("id"))
	}


def team_side_for_row(row: dict, game: dict) -> str:
	team_id = clean_text(row.get("team_id"))

	if team_id == clean_text(game.get("home_team_id")):
		return "home"

	if team_id == clean_text(game.get("away_team_id")):
		return "away"

	return ""


def main() -> None:
	parser = argparse.ArgumentParser(
		description="Aplica sugestões de resolução de jogadores."
	)

	parser.add_argument(
		"--auto",
		action="store_true",
		help="Aplica linhas com decision=auto.",
	)

	parser.add_argument(
		"--reviewed",
		action="store_true",
		help="Aplica linhas com approved=1.",
	)

	args = parser.parse_args()

	if not args.auto and not args.reviewed:
		raise SystemExit("Use --auto ou --reviewed.")

	suggestions, _ = read_csv(SUGGESTIONS_PATH)
	aliases, alias_fields = read_csv(DATA_DIR / "player_aliases.csv")
	pgs, _ = read_csv(DATA_DIR / "player_game_stats.csv")
	players, _ = read_csv(DATA_DIR / "players.csv")
	team_aliases, _ = read_csv(DATA_DIR / "team_aliases.csv")
	games, _ = read_csv(DATA_DIR / "games.csv")

	for field in REQUIRED_ALIAS_FIELDS:
		if field not in alias_fields:
			alias_fields.append(field)

	selected = []

	for row in suggestions:
		should_apply = False

		if args.auto and row.get("decision") == "auto":
			should_apply = True

		if args.reviewed and row.get("approved") == "1":
			should_apply = True

		if should_apply and clean_text(row.get("suggested_player_id")):
			selected.append(row)

	if not selected:
		print("Nenhuma sugestão selecionada para aplicar.")
		return

	existing_alias_keys = {
		(
			clean_text(row.get("player_id")),
			identity_key(row.get("alias")),
			clean_text(row.get("season_id")),
			identity_key(row.get("team_name_raw")),
			clean_text(row.get("jersey_number")),
		)
		for row in aliases
	}

	next_alias_id = next_id(aliases)
	aliases_inserted = 0

	for row in selected:
		key = (
			clean_text(row.get("suggested_player_id")),
			identity_key(row.get("player_name_raw")),
			clean_text(row.get("season_id")),
			identity_key(row.get("team_name_raw")),
			clean_text(row.get("jersey_number")),
		)

		if key in existing_alias_keys:
			continue

		aliases.append(
			{
				"id": next_alias_id,
				"player_id": clean_text(row.get("suggested_player_id")),
				"alias": clean_text(row.get("player_name_raw")),
				"alias_type": "boxscore_manual_auto",
				"season_id": clean_text(row.get("season_id")),
				"team_name_raw": clean_text(row.get("team_name_raw")),
				"jersey_number": clean_text(row.get("jersey_number")),
				"source": "player_resolution_suggestions",
				"created_at": now(),
			}
		)

		existing_alias_keys.add(key)
		next_alias_id += 1
		aliases_inserted += 1

	write_csv(DATA_DIR / "player_aliases.csv", aliases, alias_fields)

	# Recarrega aliases já com as novas linhas.
	aliases, _ = read_csv(DATA_DIR / "player_aliases.csv")

	resolver = PlayerResolver(
		players_rows=players,
		player_aliases_rows=aliases,
		team_aliases_rows=team_aliases,
	)

	games_by_id = build_game_map(games)

	updated = 0
	still_unresolved = []
	next_unresolved_id = 1

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
			updated += 1
		else:
			game = games_by_id.get(clean_text(row.get("game_id")), {})

			still_unresolved.append(
				{
					"id": next_unresolved_id,
					"game_id": clean_text(row.get("game_id")),
					"season_id": clean_text(row.get("season_id")),
					"team_id": clean_text(row.get("team_id")),
					"team_side": team_side_for_row(row, game),
					"player_name_raw": clean_text(row.get("player_name_raw")),
					"jersey_number": clean_text(row.get("jersey_number")),
					"candidate_player_ids": ",".join(candidates),
					"reason": reason,
					"source_url": clean_text(row.get("source_url")),
					"created_at": now(),
				}
			)
			next_unresolved_id += 1

	write_csv(DATA_DIR / "player_game_stats.csv", pgs, PLAYER_GAME_STATS_FIELDS)
	write_csv(
		DATA_DIR / "_runtime" / "unresolved_boxscore_players.csv",
		still_unresolved,
		UNRESOLVED_PLAYERS_FIELDS,
	)

	print(f"Sugestões aplicadas: {len(selected)}")
	print(f"Aliases inseridos: {aliases_inserted}")
	print(f"player_game_stats atualizados: {updated}")
	print(f"Ainda não resolvidos: {len(still_unresolved)}")


if __name__ == "__main__":
	main()
