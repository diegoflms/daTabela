import csv
import re
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

from src.utils.text import clean_text, identity_key, remove_accents


DATA_DIR = Path("dados")
OUT_PATH = DATA_DIR / "diagnostics" / "player_manual_review_candidates.csv"


def read_csv(path: Path) -> list[dict]:
	if not path.exists():
		return []

	with path.open("r", encoding="utf-8-sig", newline="") as file:
		return list(csv.DictReader(file))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)

	with path.open("w", encoding="utf-8", newline="") as file:
		writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
		writer.writeheader()
		writer.writerows(rows)


def norm_name(value: str) -> str:
	value = clean_text(value).replace("(T)", "")
	value = remove_accents(value.lower())
	value = re.sub(r"[^a-z0-9 ]+", " ", value)
	value = re.sub(r"\s+", " ", value).strip()
	return value


def name_similarity(a: str, b: str) -> float:
	a_norm = norm_name(a)
	b_norm = norm_name(b)

	if not a_norm or not b_norm:
		return 0.0

	if identity_key(a_norm) == identity_key(b_norm):
		return 1.0

	score = SequenceMatcher(None, a_norm, b_norm).ratio()

	a_tokens = set(a_norm.split())
	b_tokens = set(b_norm.split())

	if a_tokens and b_tokens:
		overlap = len(a_tokens & b_tokens) / max(len(a_tokens), len(b_tokens))
		score = max(score, overlap)

	if a_norm in b_tokens:
		score = max(score, 0.92)

	if b_norm in a_tokens:
		score = max(score, 0.92)

	if b_norm.startswith(a_norm + " "):
		score = max(score, 0.90)

	if a_norm.startswith(b_norm + " "):
		score = max(score, 0.90)

	return score


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


def build_candidate_index(
	players: list[dict],
	aliases: list[dict],
	team_aliases: list[dict],
) -> list[dict]:
	players_by_id = {
		clean_text(row.get("id")): row
		for row in players
		if clean_text(row.get("id"))
	}

	team_alias_map = build_team_alias_map(team_aliases)
	candidates = []

	for row in aliases:
		player_id = clean_text(row.get("player_id"))
		alias = clean_text(row.get("alias"))

		if not player_id or not alias:
			continue

		season_id = clean_text(row.get("season_id"))
		jersey_number = clean_text(row.get("jersey_number"))
		team_name_raw = clean_text(row.get("team_name_raw"))

		team_id = resolve_team_id(
			season_id=season_id,
			team_name_raw=team_name_raw,
			team_alias_map=team_alias_map,
		)

		player = players_by_id.get(player_id, {})

		candidates.append(
			{
				"player_id": player_id,
				"candidate_name": alias,
				"full_name": clean_text(player.get("full_name")),
				"display_name": clean_text(player.get("display_name")),
				"season_id": season_id,
				"team_id": team_id,
				"team_name_raw": team_name_raw,
				"jersey_number": jersey_number,
				"source": clean_text(row.get("source")) or "player_aliases",
			}
		)

	for player in players:
		player_id = clean_text(player.get("id"))

		if not player_id:
			continue

		for field in ["full_name", "display_name"]:
			name = clean_text(player.get(field))

			if not name:
				continue

			candidates.append(
				{
					"player_id": player_id,
					"candidate_name": name,
					"full_name": clean_text(player.get("full_name")),
					"display_name": clean_text(player.get("display_name")),
					"season_id": "",
					"team_id": "",
					"team_name_raw": "",
					"jersey_number": "",
					"source": f"players.{field}",
				}
			)

	return candidates


def score_candidate(
	unresolved: dict,
	candidate: dict,
) -> tuple[float, str]:
	raw_name = unresolved["player_name_raw"]
	season_id = unresolved["season_id"]
	team_id = unresolved["team_id"]
	jersey = unresolved["jersey_number"]

	name_score = name_similarity(raw_name, candidate["candidate_name"])
	score = name_score * 100

	signals = []

	if candidate["season_id"] and candidate["season_id"] == season_id:
		score += 35
		signals.append("same_season")

	if candidate["team_id"] and candidate["team_id"] == team_id:
		score += 45
		signals.append("same_team")

	if candidate["jersey_number"] and candidate["jersey_number"] == jersey:
		score += 30
		signals.append("same_jersey")

	if candidate["team_id"] and candidate["team_id"] != team_id:
		score -= 60
		signals.append("wrong_team")

	if candidate["season_id"] and candidate["season_id"] != season_id:
		score -= 15
		signals.append("wrong_season")

	if candidate["jersey_number"] and candidate["jersey_number"] != jersey:
		score -= 25
		signals.append("wrong_jersey")

	if name_score >= 0.90:
		signals.append("strong_name")

	elif name_score >= 0.75:
		signals.append("medium_name")

	else:
		signals.append("weak_name")

	return score, "|".join(signals)


def main() -> None:
	pgs = read_csv(DATA_DIR / "player_game_stats.csv")
	games = read_csv(DATA_DIR / "games.csv")
	players = read_csv(DATA_DIR / "players.csv")
	aliases = read_csv(DATA_DIR / "player_aliases.csv")
	team_aliases = read_csv(DATA_DIR / "team_aliases.csv")
	unresolved_file = read_csv(DATA_DIR / "_runtime" / "unresolved_boxscore_players.csv")

	games_by_id = {
		clean_text(row.get("id")): row
		for row in games
		if clean_text(row.get("id"))
	}

	reason_by_group = {}

	for row in unresolved_file:
		key = (
			clean_text(row.get("season_id")),
			clean_text(row.get("team_id")),
			identity_key(row.get("player_name_raw")),
			clean_text(row.get("jersey_number")),
		)
		reason_by_group[key] = clean_text(row.get("reason"))

	unresolved_rows = [
		row for row in pgs
		if not clean_text(row.get("player_id"))
	]

	groups = Counter()

	sample_by_group = {}

	for row in unresolved_rows:
		key = (
			clean_text(row.get("season_id")),
			clean_text(row.get("team_id")),
			identity_key(row.get("player_name_raw")),
			clean_text(row.get("jersey_number")),
		)

		groups[key] += 1

		if key not in sample_by_group:
			sample_by_group[key] = row

	candidates = build_candidate_index(
		players=players,
		aliases=aliases,
		team_aliases=team_aliases,
	)

	output_rows = []

	for key, count in groups.items():
		season_id, team_id, name_key, jersey = key
		sample = sample_by_group[key]

		unresolved = {
			"season_id": season_id,
			"team_id": team_id,
			"player_name_raw": clean_text(sample.get("player_name_raw")),
			"jersey_number": jersey,
		}

		scored = []

		for candidate in candidates:
			score, signals = score_candidate(unresolved, candidate)

			# Mantém candidatos razoáveis.
			if score < 65:
				continue

			scored.append((score, signals, candidate))

		scored.sort(key=lambda item: item[0], reverse=True)

		top = scored[:8]

		if not top:
			output_rows.append(
				{
					"approved": "",
					"group_id": f"{season_id}|{team_id}|{name_key}|{jersey}",
					"season_id": season_id,
					"team_id": team_id,
					"team_name_raw": game_team_name(sample, games_by_id),
					"player_name_raw": clean_text(sample.get("player_name_raw")),
					"jersey_number": jersey,
					"unresolved_rows": count,
					"current_reason": reason_by_group.get(key, ""),
					"candidate_rank": "",
					"candidate_player_id": "",
					"candidate_full_name": "",
					"candidate_display_name": "",
					"matched_alias": "",
					"score": "",
					"signals": "no_candidate",
					"candidate_alias_team": "",
					"candidate_alias_season": "",
					"candidate_alias_jersey": "",
					"source": "",
					"sample_game_id": clean_text(sample.get("game_id")),
					"sample_boxscore_url": clean_text(sample.get("source_url")),
				}
			)
			continue

		for rank, (score, signals, candidate) in enumerate(top, start=1):
			output_rows.append(
				{
					"approved": "",
					"group_id": f"{season_id}|{team_id}|{name_key}|{jersey}",
					"season_id": season_id,
					"team_id": team_id,
					"team_name_raw": game_team_name(sample, games_by_id),
					"player_name_raw": clean_text(sample.get("player_name_raw")),
					"jersey_number": jersey,
					"unresolved_rows": count,
					"current_reason": reason_by_group.get(key, ""),
					"candidate_rank": rank,
					"candidate_player_id": candidate["player_id"],
					"candidate_full_name": candidate["full_name"],
					"candidate_display_name": candidate["display_name"],
					"matched_alias": candidate["candidate_name"],
					"score": f"{score:.2f}",
					"signals": signals,
					"candidate_alias_team": candidate["team_name_raw"],
					"candidate_alias_season": candidate["season_id"],
					"candidate_alias_jersey": candidate["jersey_number"],
					"source": candidate["source"],
					"sample_game_id": clean_text(sample.get("game_id")),
					"sample_boxscore_url": clean_text(sample.get("source_url")),
				}
			)

	fieldnames = [
		"approved",
		"group_id",
		"season_id",
		"team_id",
		"team_name_raw",
		"player_name_raw",
		"jersey_number",
		"unresolved_rows",
		"current_reason",
		"candidate_rank",
		"candidate_player_id",
		"candidate_full_name",
		"candidate_display_name",
		"matched_alias",
		"score",
		"signals",
		"candidate_alias_team",
		"candidate_alias_season",
		"candidate_alias_jersey",
		"source",
		"sample_game_id",
		"sample_boxscore_url",
	]

	output_rows.sort(
		key=lambda row: (
			row["season_id"],
			row["team_id"],
			row["player_name_raw"],
			int(row["candidate_rank"] or 999),
		)
	)

	write_csv(OUT_PATH, output_rows, fieldnames)

	print(f"Arquivo gerado em: {OUT_PATH}")
	print(f"Grupos pendentes: {len(groups)}")
	print(f"Linhas no arquivo: {len(output_rows)}")
	print(f"Grupos sem candidato: {sum(1 for row in output_rows if row['signals'] == 'no_candidate')}")


if __name__ == "__main__":
	main()
