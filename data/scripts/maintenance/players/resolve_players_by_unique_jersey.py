import argparse
import csv
from collections import defaultdict
from difflib import SequenceMatcher
import re
from datetime import datetime
from pathlib import Path

from src.scraping.boxscores_scraper import (
	PLAYER_GAME_STATS_FIELDS,
	UNRESOLVED_PLAYERS_FIELDS,
	PlayerResolver,
)
from src.utils.text import clean_text, identity_key, remove_accents


DATA_DIR = Path("dados")
REPORT_PATH = DATA_DIR / "diagnostics" / "player_unique_jersey_resolutions.csv"


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

def norm_name(value: str) -> str:
	value = clean_text(value)
	value = value.replace("(T)", "")
	value = remove_accents(value.lower())
	value = re.sub(r"[^a-z0-9 ]+", " ", value)
	value = re.sub(r"\s+", " ", value).strip()
	return value


def name_score(raw_name: str, candidate_names: set[str]) -> tuple[float, str]:
	raw = norm_name(raw_name)

	if not raw:
		return 0.0, ""

	raw_key = identity_key(raw)
	raw_tokens = set(raw.split())

	best_score = 0.0
	best_name = ""

	for candidate in candidate_names:
		cand = norm_name(candidate)

		if not cand:
			continue

		cand_key = identity_key(cand)
		cand_tokens = set(cand.split())

		score = SequenceMatcher(None, raw, cand).ratio()

		if raw_key == cand_key:
			score = 1.0

		# Ex: "Andre" em "Andre Luiz Bresolin Goes"
		elif raw in cand_tokens:
			score = max(score, 0.93)

		# Ex: "Borges" em "Isaque Duarte Borges"
		elif raw_tokens and raw_tokens.issubset(cand_tokens):
			score = max(score, 0.93)

		# Ex: "Lucas" e "Lucas Lima"
		elif cand.startswith(raw + " "):
			score = max(score, 0.90)

		if score > best_score:
			best_score = score
			best_name = candidate

	return best_score, best_name

def build_team_alias_map(team_aliases: list[dict]) -> dict[tuple[str, str], str]:
	result = {}

	for row in team_aliases:
		team_id = clean_text(row.get("team_id"))
		season_id = clean_text(row.get("season_id"))
		alias = clean_text(row.get("alias"))

		if not team_id or not alias:
			continue

		result[(season_id, identity_key(alias))] = team_id
		result[("", identity_key(alias))] = team_id

	return result


def resolve_team_id(
	season_id: str,
	team_name_raw: str,
	team_alias_map: dict[tuple[str, str], str],
) -> str:
	key = identity_key(team_name_raw)

	if not key:
		return ""

	return team_alias_map.get((season_id, key)) or team_alias_map.get(("", key), "")


def game_team_name(row: dict, games_by_id: dict[str, dict]) -> str:
	game = games_by_id.get(clean_text(row.get("game_id")), {})
	team_id = clean_text(row.get("team_id"))

	if team_id == clean_text(game.get("home_team_id")):
		return clean_text(game.get("home_team_name_raw"))

	if team_id == clean_text(game.get("away_team_id")):
		return clean_text(game.get("away_team_name_raw"))

	return ""


def team_side_for_row(row: dict, games_by_id: dict[str, dict]) -> str:
	game = games_by_id.get(clean_text(row.get("game_id")), {})
	team_id = clean_text(row.get("team_id"))

	if team_id == clean_text(game.get("home_team_id")):
		return "home"

	if team_id == clean_text(game.get("away_team_id")):
		return "away"

	return ""


def build_unique_jersey_candidates(
	aliases: list[dict],
	team_aliases: list[dict],
	players_by_id: dict[str, dict],
) -> dict[tuple[str, str, str], dict[str, set[str]]]:
	team_alias_map = build_team_alias_map(team_aliases)
	result = defaultdict(lambda: defaultdict(set))

	for row in aliases:
		player_id = clean_text(row.get("player_id"))
		season_id = clean_text(row.get("season_id"))
		jersey_number = clean_text(row.get("jersey_number"))
		team_name_raw = clean_text(row.get("team_name_raw"))
		alias = clean_text(row.get("alias"))

		if not player_id or not season_id or not jersey_number or not team_name_raw:
			continue

		team_id = resolve_team_id(
			season_id=season_id,
			team_name_raw=team_name_raw,
			team_alias_map=team_alias_map,
		)

		if not team_id:
			continue

		key = (season_id, team_id, jersey_number)

		if alias:
			result[key][player_id].add(alias)

		player = players_by_id.get(player_id, {})

		if clean_text(player.get("full_name")):
			result[key][player_id].add(clean_text(player.get("full_name")))

		if clean_text(player.get("display_name")):
			result[key][player_id].add(clean_text(player.get("display_name")))

	return result

def main() -> None:
	parser = argparse.ArgumentParser(
		description="Resolve jogadores por combinação única temporada + time + camisa."
	)

	parser.add_argument(
		"--apply",
		action="store_true",
		help="Aplica as resoluções. Sem isso, só gera relatório.",
	)

	args = parser.parse_args()

	pgs, _ = read_csv(DATA_DIR / "player_game_stats.csv")
	aliases, alias_fields = read_csv(DATA_DIR / "player_aliases.csv")
	players, _ = read_csv(DATA_DIR / "players.csv")
	team_aliases, _ = read_csv(DATA_DIR / "team_aliases.csv")
	games, _ = read_csv(DATA_DIR / "games.csv")

	for field in ALIAS_REQUIRED_FIELDS:
		if field not in alias_fields:
			alias_fields.append(field)

	players_by_id = {
		clean_text(row.get("id")): row
		for row in players
		if clean_text(row.get("id"))
	}

	games_by_id = {
		clean_text(row.get("id")): row
		for row in games
		if clean_text(row.get("id"))
	}

	unique_jersey_candidates = build_unique_jersey_candidates(
		aliases=aliases,
		team_aliases=team_aliases,
		players_by_id=players_by_id,
	)

	unresolved_rows = [
		row for row in pgs
		if not clean_text(row.get("player_id"))
	]

	report_by_group = {}

	for row in unresolved_rows:
		season_id = clean_text(row.get("season_id"))
		team_id = clean_text(row.get("team_id"))
		jersey_number = clean_text(row.get("jersey_number"))
		player_name_raw = clean_text(row.get("player_name_raw"))

		key = (
			season_id,
			team_id,
			jersey_number,
			identity_key(player_name_raw),
		)

		candidate_map = unique_jersey_candidates.get(
			(season_id, team_id, jersey_number),
			{},
		)

		candidate_ids = set(candidate_map.keys())

		if key not in report_by_group:
			report_by_group[key] = {
				"decision": "",
				"season_id": season_id,
				"team_id": team_id,
				"team_name_raw": game_team_name(row, games_by_id),
				"jersey_number": jersey_number,
				"player_name_raw": player_name_raw,
				"unresolved_rows": 0,
				"candidate_player_ids": ",".join(sorted(candidate_ids)),
				"resolved_player_id": "",
				"resolved_full_name": "",
				"resolved_display_name": "",
				"reason": "",
				"sample_game_id": clean_text(row.get("game_id")),
				"sample_boxscore_url": clean_text(row.get("source_url")),
			}

		report_by_group[key]["unresolved_rows"] += 1

		if len(candidate_ids) == 1:
			player_id = next(iter(candidate_ids))
			player = players_by_id.get(player_id, {})
			candidate_names = candidate_map.get(player_id, set())

			score, matched_name = name_score(player_name_raw, candidate_names)

			report_by_group[key]["resolved_player_id"] = player_id
			report_by_group[key]["resolved_full_name"] = clean_text(player.get("full_name"))
			report_by_group[key]["resolved_display_name"] = clean_text(player.get("display_name"))

			if score >= 0.88:
				report_by_group[key]["decision"] = "auto"
				report_by_group[key]["reason"] = f"unique_jersey_name_match:{score:.2f}:{matched_name}"
			else:
				report_by_group[key]["decision"] = "manual"
				report_by_group[key]["reason"] = f"unique_jersey_but_name_mismatch:{score:.2f}:{matched_name}"

		elif len(candidate_ids) > 1:
			report_by_group[key]["decision"] = "manual"
			report_by_group[key]["reason"] = "jersey_not_unique"

		else:
			report_by_group[key]["decision"] = "manual"
			report_by_group[key]["reason"] = "no_candidate_for_jersey"

	report_rows = list(report_by_group.values())

	report_rows.sort(
		key=lambda row: (
			row["decision"] != "auto",
			-int(row["unresolved_rows"]),
			row["season_id"],
			row["team_id"],
			row["jersey_number"],
		)
	)

	fieldnames = [
		"decision",
		"season_id",
		"team_id",
		"team_name_raw",
		"jersey_number",
		"player_name_raw",
		"unresolved_rows",
		"candidate_player_ids",
		"resolved_player_id",
		"resolved_full_name",
		"resolved_display_name",
		"reason",
		"sample_game_id",
		"sample_boxscore_url",
	]

	write_csv(REPORT_PATH, report_rows, fieldnames)

	auto_rows = [
		row for row in report_rows
		if row["decision"] == "auto"
		and clean_text(row["resolved_player_id"])
	]

	print(f"Relatório gerado em: {REPORT_PATH}")
	print(f"Grupos não resolvidos: {len(report_rows)}")
	print(f"Grupos auto por camisa única: {len(auto_rows)}")
	print(f"Linhas cobertas por auto: {sum(int(row['unresolved_rows']) for row in auto_rows)}")

	if not args.apply:
		print("\nNada foi aplicado. Rode com --apply para aplicar.")
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

	for row in auto_rows:
		alias_key = (
			clean_text(row["resolved_player_id"]),
			identity_key(row["player_name_raw"]),
			clean_text(row["season_id"]),
			identity_key(row["team_name_raw"]),
			clean_text(row["jersey_number"]),
		)

		if alias_key in existing_alias_keys:
			continue

		aliases.append(
			{
				"id": next_alias_id,
				"player_id": clean_text(row["resolved_player_id"]),
				"alias": clean_text(row["player_name_raw"]),
				"alias_type": "boxscore_unique_jersey",
				"season_id": clean_text(row["season_id"]),
				"team_name_raw": clean_text(row["team_name_raw"]),
				"jersey_number": clean_text(row["jersey_number"]),
				"source": "resolve_players_by_unique_jersey",
				"created_at": now(),
			}
		)

		existing_alias_keys.add(alias_key)
		next_alias_id += 1
		aliases_inserted += 1

	write_csv(DATA_DIR / "player_aliases.csv", aliases, alias_fields)

	# Recarrega aliases e usa o resolver oficial.
	aliases, _ = read_csv(DATA_DIR / "player_aliases.csv")

	resolver = PlayerResolver(
		players_rows=players,
		player_aliases_rows=aliases,
		team_aliases_rows=team_aliases,
	)

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

	print("\nAplicado.")
	print(f"Aliases inseridos: {aliases_inserted}")
	print(f"player_game_stats atualizados: {updated}")
	print(f"Ainda não resolvidos: {len(still_unresolved)}")


if __name__ == "__main__":
	main()
