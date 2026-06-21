import csv
import re
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

from src.utils.text import clean_text, identity_key, remove_accents


DATA_DIR = Path("dados")
OUT_PATH = DATA_DIR / "diagnostics" / "player_resolution_suggestions.csv"


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
	value = clean_text(value)
	value = value.replace("(T)", "")
	value = remove_accents(value.lower())
	value = re.sub(r"[^a-z0-9 ]+", " ", value)
	value = re.sub(r"\s+", " ", value).strip()
	return value


def similarity(a: str, b: str) -> float:
	a = norm_name(a)
	b = norm_name(b)

	if not a or not b:
		return 0.0

	if a == b:
		return 1.0

	a_key = identity_key(a)
	b_key = identity_key(b)

	if a_key == b_key:
		return 1.0

	score = SequenceMatcher(None, a, b).ratio()

	a_tokens = set(a.split())
	b_tokens = set(b.split())

	if a_tokens and b_tokens:
		overlap = len(a_tokens & b_tokens) / max(len(a_tokens), len(b_tokens))
		score = max(score, overlap)

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


def resolve_alias_team_id(row: dict, team_alias_map: dict[tuple[str, str], str]) -> str:
	season_id = clean_text(row.get("season_id"))
	team_name = clean_text(row.get("team_name_raw"))

	if not team_name:
		return ""

	key = identity_key(team_name)

	return team_alias_map.get((season_id, key)) or team_alias_map.get(("", key), "")


def main() -> None:
	pgs = read_csv(DATA_DIR / "player_game_stats.csv")
	games = read_csv(DATA_DIR / "games.csv")
	players = read_csv(DATA_DIR / "players.csv")
	aliases = read_csv(DATA_DIR / "player_aliases.csv")
	team_aliases = read_csv(DATA_DIR / "team_aliases.csv")

	games_by_id = {row["id"]: row for row in games if row.get("id")}
	players_by_id = {row["id"]: row for row in players if row.get("id")}
	team_alias_map = build_team_alias_map(team_aliases)

	unresolved_rows = [
		row for row in pgs
		if not clean_text(row.get("player_id"))
	]

	groups = Counter()

	for row in unresolved_rows:
		key = (
			clean_text(row.get("season_id")),
			clean_text(row.get("team_id")),
			clean_text(row.get("player_name_raw")),
			clean_text(row.get("jersey_number")),
		)
		groups[key] += 1

	candidate_rows = []

	for row in aliases:
		player_id = clean_text(row.get("player_id"))
		alias = clean_text(row.get("alias"))

		if not player_id or not alias:
			continue

		candidate_rows.append(
			{
				"player_id": player_id,
				"candidate_name": alias,
				"full_name": clean_text(players_by_id.get(player_id, {}).get("full_name")),
				"display_name": clean_text(players_by_id.get(player_id, {}).get("display_name")),
				"season_id": clean_text(row.get("season_id")),
				"team_id": resolve_alias_team_id(row, team_alias_map),
				"team_name_raw": clean_text(row.get("team_name_raw")),
				"jersey_number": clean_text(row.get("jersey_number")),
				"source": clean_text(row.get("source")) or "player_aliases",
			}
		)

	for player in players:
		player_id = clean_text(player.get("id"))

		if not player_id:
			continue

		for name_field in ["full_name", "display_name"]:
			name = clean_text(player.get(name_field))

			if not name:
				continue

			candidate_rows.append(
				{
					"player_id": player_id,
					"candidate_name": name,
					"full_name": clean_text(player.get("full_name")),
					"display_name": clean_text(player.get("display_name")),
					"season_id": "",
					"team_id": "",
					"team_name_raw": "",
					"jersey_number": "",
					"source": f"players.{name_field}",
				}
			)

	suggestions = []

	for (season_id, team_id, player_name_raw, jersey_number), count in groups.items():
		scored = []

		for candidate in candidate_rows:
			sim = similarity(player_name_raw, candidate["candidate_name"])

			if sim < 0.72:
				continue

			score = sim * 100

			c_season = candidate["season_id"]
			c_team = candidate["team_id"]
			c_jersey = candidate["jersey_number"]

			same_season = bool(c_season and c_season == season_id)
			same_team = bool(c_team and c_team == team_id)
			same_jersey = bool(c_jersey and c_jersey == jersey_number)

			wrong_team = bool(c_team and team_id and c_team != team_id)
			wrong_jersey = bool(c_jersey and jersey_number and c_jersey != jersey_number)

			if same_season:
				score += 25

			if same_team:
				score += 30

			if same_jersey:
				score += 20

			if wrong_team:
				score -= 45

			if wrong_jersey:
				score -= 20

			scored.append((score, candidate, sim))

		scored.sort(key=lambda item: item[0], reverse=True)

		best = scored[0] if scored else None
		second = scored[1] if len(scored) > 1 else None

		if not best:
			suggestions.append(
				{
					"decision": "manual",
					"reason": "no_candidate",
					"approved": "",
					"season_id": season_id,
					"team_id": team_id,
					"player_name_raw": player_name_raw,
					"jersey_number": jersey_number,
					"unresolved_rows": count,
					"suggested_player_id": "",
					"suggested_full_name": "",
					"suggested_display_name": "",
					"matched_alias": "",
					"score": "",
					"second_score": "",
					"source": "",
					"team_name_raw": "",
					"sample_game_id": "",
					"sample_boxscore_url": "",
				}
			)
			continue

		best_score, candidate, sim = best
		second_score = second[0] if second else 0
		margin = best_score - second_score

		# Regra conservadora:
		# precisa ter match forte e alguma evidência contextual.
		has_context = (
			candidate["season_id"] == season_id
			or candidate["team_id"] == team_id
			or candidate["jersey_number"] == jersey_number
		)

		decision = "manual"
		reason = "needs_review"

		if best_score >= 130 and margin >= 12 and has_context:
			decision = "auto"
			reason = "high_confidence"

		if best_score >= 150 and margin >= 6 and has_context:
			decision = "auto"
			reason = "very_high_confidence"

		sample_row = next(
			row for row in unresolved_rows
			if clean_text(row.get("season_id")) == season_id
			and clean_text(row.get("team_id")) == team_id
			and clean_text(row.get("player_name_raw")) == player_name_raw
			and clean_text(row.get("jersey_number")) == jersey_number
		)

		sample_game = games_by_id.get(clean_text(sample_row.get("game_id")), {})
		team_name_raw = ""

		if clean_text(sample_game.get("home_team_id")) == team_id:
			team_name_raw = clean_text(sample_game.get("home_team_name_raw"))
		elif clean_text(sample_game.get("away_team_id")) == team_id:
			team_name_raw = clean_text(sample_game.get("away_team_name_raw"))

		suggestions.append(
			{
				"decision": decision,
				"reason": reason,
				"approved": "",
				"season_id": season_id,
				"team_id": team_id,
				"player_name_raw": player_name_raw,
				"jersey_number": jersey_number,
				"unresolved_rows": count,
				"suggested_player_id": candidate["player_id"],
				"suggested_full_name": candidate["full_name"],
				"suggested_display_name": candidate["display_name"],
				"matched_alias": candidate["candidate_name"],
				"score": f"{best_score:.2f}",
				"second_score": f"{second_score:.2f}",
				"source": candidate["source"],
				"team_name_raw": team_name_raw,
				"sample_game_id": clean_text(sample_row.get("game_id")),
				"sample_boxscore_url": clean_text(sample_row.get("source_url")),
			}
		)

	fieldnames = [
		"decision",
		"reason",
		"approved",
		"season_id",
		"team_id",
		"player_name_raw",
		"jersey_number",
		"unresolved_rows",
		"suggested_player_id",
		"suggested_full_name",
		"suggested_display_name",
		"matched_alias",
		"score",
		"second_score",
		"source",
		"team_name_raw",
		"sample_game_id",
		"sample_boxscore_url",
	]

	suggestions.sort(
		key=lambda row: (
			row["decision"] != "auto",
			-int(row["unresolved_rows"]),
			row["season_id"],
			row["team_id"],
			row["player_name_raw"],
		)
	)

	write_csv(OUT_PATH, suggestions, fieldnames)

	print(f"Arquivo gerado em: {OUT_PATH}")
	print(f"Grupos não resolvidos: {len(suggestions)}")
	print(f"Auto: {sum(1 for row in suggestions if row['decision'] == 'auto')}")
	print(f"Manual: {sum(1 for row in suggestions if row['decision'] == 'manual')}")
	print(f"Linhas cobertas por auto: {sum(int(row['unresolved_rows']) for row in suggestions if row['decision'] == 'auto')}")


if __name__ == "__main__":
	main()