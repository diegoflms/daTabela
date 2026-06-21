from collections import Counter, defaultdict
from pathlib import Path

from src.transformations.stats_helpers import (
	COMMON_STAT_OUTPUT_FIELDS,
	add_totals,
	build_indexes,
	empty_totals,
	player_name,
	season_name,
	sort_int,
	stat_output,
	team_name,
)
from src.utils.csv_io import read_csv_dicts, write_csv_dicts
from src.utils.text import clean_text


DATA_DIR = Path("dados")


PLAYER_SEASONS_FIELDS = [
	"id",
	"season_id",
	"season_name",
	"player_id",
	"player_name",
	"teams_count",
	"team_ids",
	"team_names",
	"primary_team_id",
	"primary_team_name",
	"games_played",
	"games_started",
	*COMMON_STAT_OUTPUT_FIELDS,
]


def build_player_seasons(data_dir: Path = DATA_DIR) -> dict:
	player_team_seasons = read_csv_dicts(data_dir / "player_team_seasons.csv")
	players_by_id, teams_by_id, seasons_by_id = build_indexes(data_dir)

	groups = {}

	for row in player_team_seasons:
		season_id = clean_text(row.get("season_id"))
		player_id = clean_text(row.get("player_id"))
		team_id = clean_text(row.get("team_id"))

		if not season_id or not player_id:
			continue

		key = (season_id, player_id)

		if key not in groups:
			groups[key] = {
				"season_id": season_id,
				"player_id": player_id,
				"team_games": Counter(),
				"games_played": 0,
				"games_started": 0,
				"totals": empty_totals(),
			}

		group = groups[key]

		games_played = int(row.get("games_played") or 0)

		group["games_played"] += games_played
		group["games_started"] += int(row.get("games_started") or 0)

		if team_id:
			group["team_games"][team_id] += games_played

		add_totals(group["totals"], row)

	output_rows = []

	sorted_groups = sorted(
		groups.values(),
		key=lambda group: (
			sort_int(group["season_id"]),
			player_name(players_by_id.get(group["player_id"], {})).lower(),
		),
	)

	for idx, group in enumerate(sorted_groups, start=1):
		season_id = group["season_id"]
		player_id = group["player_id"]

		team_ids = list(group["team_games"].keys())
		primary_team_id = ""

		if group["team_games"]:
			primary_team_id = group["team_games"].most_common(1)[0][0]

		team_names = [
			team_name(teams_by_id.get(team_id, {}))
			for team_id in team_ids
		]

		row = {
			"id": idx,
			"season_id": season_id,
			"season_name": season_name(seasons_by_id.get(season_id, {})),
			"player_id": player_id,
			"player_name": player_name(players_by_id.get(player_id, {})),
			"teams_count": len(team_ids),
			"team_ids": "|".join(team_ids),
			"team_names": "|".join(team_names),
			"primary_team_id": primary_team_id,
			"primary_team_name": team_name(teams_by_id.get(primary_team_id, {})),
			"games_played": group["games_played"],
			"games_started": group["games_started"],
		}

		row.update(stat_output(group["totals"], group["games_played"]))
		output_rows.append(row)

	output_path = data_dir / "player_seasons.csv"

	write_csv_dicts(output_path, PLAYER_SEASONS_FIELDS, output_rows)

	return {
		"output_path": output_path,
		"input_rows": len(player_team_seasons),
		"output_rows": len(output_rows),
	}