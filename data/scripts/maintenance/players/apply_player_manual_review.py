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
REVIEW_PATH = DATA_DIR / "diagnostics" / "player_manual_review_candidates.csv"


ALIAS_REQUIRED_FIELDS = [
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


def team_side_for_row(row: dict, games_by_id: dict[str, dict]) -> str:
	game = games_by_id.get(clean_text(row.get("game_id")), {})
	team_id = clean_text(row.get("team_id"))

	if team_id == clean_text(game.get("home_team_id")):
		return "home"

	if team_id == clean_text(game.get("away_team_id")):
		return "away"

	return ""


def main() -> None:
	review_rows, _ = read_csv(REVIEW_PATH)
	pgs, _ = read_csv(DATA_DIR / "player_game_stats.csv")
	aliases, alias_fields = read_csv(DATA_DIR / "player_aliases.csv")
	players, _ = read_csv(DATA_DIR / "players.csv")
	team_aliases, _ = read_csv(DATA_DIR / "team_aliases.csv")
	games, _ = read_csv(DATA_DIR / "games.csv")

	for field in ALIAS_REQUIRED_FIELDS:
		if field not in alias_fields:
			alias_fields.append(field)

	approved = [
		row for row in review_rows
		if clean_text(row.get("approved")) == "1"
		and clean_text(row.get("candidate_player_id"))
	]

	if not approved:
		print("Nenhuma linha aprovada encontrada.")
		return

	# Impede dois aprovados no mesmo grupo.
	group_counts = {}

	for row in approved:
		group_id = clean_text(row.get("group_id"))
		group_counts[group_id] = group_counts.get(group_id, 0) + 1

	duplicated_groups = [
		group_id for group_id, count in group_counts.items()
		if count > 1
	]

	if duplicated_groups:
		print("Erro: existem grupos com mais de uma linha approved=1.")
		print("Corrija estes group_id:")
		for group_id in duplicated_groups[:20]:
			print(group_id)
		raise SystemExit(1)

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
	inserted_aliases = 0

	for row in approved:
		player_id = clean_text(row.get("candidate_player_id"))
		alias = clean_text(row.get("player_name_raw"))
		season_id = clean_text(row.get("season_id"))
		team_name_raw = clean_text(row.get("team_name_raw"))
		jersey_number = clean_text(row.get("jersey_number"))

		key = (
			player_id,
			identity_key(alias),
			season_id,
			identity_key(team_name_raw),
			jersey_number,
		)

		if key in existing_alias_keys:
			continue

		aliases.append(
			{
				"id": next_alias_id,
				"player_id": player_id,
				"alias": alias,
				"alias_type": "boxscore_manual_review",
				"season_id": season_id,
				"team_name_raw": team_name_raw,
				"jersey_number": jersey_number,
				"source": "player_manual_review_candidates",
				"created_at": now(),
			}
		)

		existing_alias_keys.add(key)
		next_alias_id += 1
		inserted_aliases += 1

	write_csv(DATA_DIR / "player_aliases.csv", aliases, alias_fields)

	aliases, _ = read_csv(DATA_DIR / "player_aliases.csv")

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
			still_unresolved.append(
				{
					"id": next_unresolved_id,
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
			next_unresolved_id += 1

	write_csv(DATA_DIR / "player_game_stats.csv", pgs, PLAYER_GAME_STATS_FIELDS)
	write_csv(
		DATA_DIR / "_runtime" / "unresolved_boxscore_players.csv",
		still_unresolved,
		UNRESOLVED_PLAYERS_FIELDS,
	)

	print(f"Linhas aprovadas: {len(approved)}")
	print(f"Aliases inseridos: {inserted_aliases}")
	print(f"player_game_stats atualizados: {updated}")
	print(f"Ainda não resolvidos: {len(still_unresolved)}")


if __name__ == "__main__":
	main()
