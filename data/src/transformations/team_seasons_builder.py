from collections import defaultdict
from pathlib import Path

from src.transformations.stats_helpers import (
	as_float,
	build_indexes,
	fmt_int,
	fmt_pct,
	per_game,
	season_name,
	sort_int,
	team_name,
)
from src.utils.csv_io import read_csv_dicts, write_csv_dicts
from src.utils.text import clean_text


DATA_DIR = Path("dados")


TEAM_SEASONS_FIELDS = [
	"id",
	"season_id",
	"season_name",
	"competition",
	"team_id",
	"team_name",
	"rank",
	"ap_pct",
	"wins",
	"losses",
	"home_record",
	"away_record",
	"finish_stage",
	"is_champion",
	"games_played",
	"points_total",
	"points_per_game",
	"points_against",
	"point_diff",
	"fg_made",
	"fg_attempted",
	"fg_pct",
	"three_made",
	"three_attempted",
	"three_pct",
	"two_made",
	"two_attempted",
	"two_pct",
	"ft_made",
	"ft_attempted",
	"ft_pct",
	"offensive_rebounds_total",
	"defensive_rebounds_total",
	"rebounds_total",
	"rebounds_per_game",
	"assists_total",
	"assists_per_game",
	"steals_total",
	"steals_per_game",
	"blocks_total",
	"blocks_per_game",
	"turnovers_total",
	"turnovers_per_game",
	"fouls_committed_total",
	"fouls_received_total",
	"dunks_total",
	"plus_minus_total",
	"plus_minus_per_game",
	"efficiency_total",
	"efficiency_per_game",
]


TEAM_INPUT_TO_TOTAL = {
	"points": "points_total",
	"fg_made": "fg_made",
	"fg_attempted": "fg_attempted",
	"three_made": "three_made",
	"three_attempted": "three_attempted",
	"two_made": "two_made",
	"two_attempted": "two_attempted",
	"ft_made": "ft_made",
	"ft_attempted": "ft_attempted",
	"offensive_rebounds": "offensive_rebounds_total",
	"defensive_rebounds": "defensive_rebounds_total",
	"total_rebounds": "rebounds_total",
	"assists": "assists_total",
	"steals": "steals_total",
	"blocks": "blocks_total",
	"turnovers": "turnovers_total",
	"fouls_committed": "fouls_committed_total",
	"fouls_received": "fouls_received_total",
	"dunks": "dunks_total",
	"plus_minus": "plus_minus_total",
	"efficiency": "efficiency_total",
}


TEAM_TOTAL_FIELDS = list(TEAM_INPUT_TO_TOTAL.values())


def empty_team_group(season_id: str, competition: str, team_id: str) -> dict:
	return {
		"season_id": season_id,
		"competition": competition,
		"team_id": team_id,
		"game_ids": set(),
		"totals": {field: 0.0 for field in TEAM_TOTAL_FIELDS},
	}


def standings_index(standings: list[dict]) -> dict[tuple[str, str, str], dict]:
	result = {}

	for row in standings:
		season_id = clean_text(row.get("season_id"))
		competition = clean_text(row.get("competition")) or "NBB"
		team_id = clean_text(row.get("team_id"))

		if season_id and team_id:
			result[(season_id, competition, team_id)] = row

	return result


def build_team_seasons(data_dir: Path = DATA_DIR) -> dict:
	team_game_stats = read_csv_dicts(data_dir / "team_game_stats.csv")
	standings = read_csv_dicts(data_dir / "standings.csv")
	_players_by_id, teams_by_id, seasons_by_id = build_indexes(data_dir)

	standings_by_key = standings_index(standings)
	groups = {}

	for row in team_game_stats:
		season_id = clean_text(row.get("season_id"))
		competition = clean_text(row.get("competition")) or "NBB"
		team_id = clean_text(row.get("team_id"))
		game_id = clean_text(row.get("game_id"))

		if not season_id or not team_id:
			continue

		key = (season_id, competition, team_id)

		if key not in groups:
			groups[key] = empty_team_group(season_id, competition, team_id)

		group = groups[key]

		if game_id:
			group["game_ids"].add(game_id)

		for input_field, total_field in TEAM_INPUT_TO_TOTAL.items():
			group["totals"][total_field] += as_float(row.get(input_field))

	output_rows = []

	sorted_groups = sorted(
		groups.values(),
		key=lambda group: (
			sort_int(group["season_id"]),
			group["competition"],
			team_name(teams_by_id.get(group["team_id"], {})).lower(),
		),
	)

	for idx, group in enumerate(sorted_groups, start=1):
		season_id = group["season_id"]
		competition = group["competition"]
		team_id = group["team_id"]

		totals = group["totals"]
		games_played = len(group["game_ids"])

		st = standings_by_key.get((season_id, competition, team_id), {})

		fg_made = totals["fg_made"]
		fg_attempted = totals["fg_attempted"]

		three_made = totals["three_made"]
		three_attempted = totals["three_attempted"]

		two_made = totals["two_made"]
		two_attempted = totals["two_attempted"]

		ft_made = totals["ft_made"]
		ft_attempted = totals["ft_attempted"]

		row = {
			"id": idx,
			"season_id": season_id,
			"season_name": season_name(seasons_by_id.get(season_id, {})),
			"competition": competition,
			"team_id": team_id,
			"team_name": team_name(teams_by_id.get(team_id, {})),
			"rank": clean_text(st.get("rank")),
			"ap_pct": clean_text(st.get("ap_pct")),
			"wins": clean_text(st.get("wins")),
			"losses": clean_text(st.get("losses")),
			"home_record": clean_text(st.get("home_record")),
			"away_record": clean_text(st.get("away_record")),
			"finish_stage": clean_text(st.get("finish_stage")),
			"is_champion": clean_text(st.get("is_champion")),
			"games_played": games_played,
			"points_total": fmt_int(totals["points_total"]),
			"points_per_game": per_game(totals["points_total"], games_played),
			"points_against": clean_text(st.get("points_against")),
			"point_diff": clean_text(st.get("point_diff")),
			"fg_made": fmt_int(fg_made),
			"fg_attempted": fmt_int(fg_attempted),
			"fg_pct": fmt_pct(fg_made, fg_attempted),
			"three_made": fmt_int(three_made),
			"three_attempted": fmt_int(three_attempted),
			"three_pct": fmt_pct(three_made, three_attempted),
			"two_made": fmt_int(two_made),
			"two_attempted": fmt_int(two_attempted),
			"two_pct": fmt_pct(two_made, two_attempted),
			"ft_made": fmt_int(ft_made),
			"ft_attempted": fmt_int(ft_attempted),
			"ft_pct": fmt_pct(ft_made, ft_attempted),
			"offensive_rebounds_total": fmt_int(totals["offensive_rebounds_total"]),
			"defensive_rebounds_total": fmt_int(totals["defensive_rebounds_total"]),
			"rebounds_total": fmt_int(totals["rebounds_total"]),
			"rebounds_per_game": per_game(totals["rebounds_total"], games_played),
			"assists_total": fmt_int(totals["assists_total"]),
			"assists_per_game": per_game(totals["assists_total"], games_played),
			"steals_total": fmt_int(totals["steals_total"]),
			"steals_per_game": per_game(totals["steals_total"], games_played),
			"blocks_total": fmt_int(totals["blocks_total"]),
			"blocks_per_game": per_game(totals["blocks_total"], games_played),
			"turnovers_total": fmt_int(totals["turnovers_total"]),
			"turnovers_per_game": per_game(totals["turnovers_total"], games_played),
			"fouls_committed_total": fmt_int(totals["fouls_committed_total"]),
			"fouls_received_total": fmt_int(totals["fouls_received_total"]),
			"dunks_total": fmt_int(totals["dunks_total"]),
			"plus_minus_total": fmt_int(totals["plus_minus_total"]),
			"plus_minus_per_game": per_game(totals["plus_minus_total"], games_played),
			"efficiency_total": fmt_int(totals["efficiency_total"]),
			"efficiency_per_game": per_game(totals["efficiency_total"], games_played),
		}

		output_rows.append(row)

	output_path = data_dir / "team_seasons.csv"

	write_csv_dicts(output_path, TEAM_SEASONS_FIELDS, output_rows)

	return {
		"output_path": output_path,
		"input_rows": len(team_game_stats),
		"output_rows": len(output_rows),
	}