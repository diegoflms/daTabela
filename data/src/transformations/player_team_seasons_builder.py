from collections import Counter, defaultdict
from pathlib import Path

from src.utils.csv_io import read_csv_dicts, write_csv_dicts
from src.utils.text import clean_text


DATA_DIR = Path("dados")


PLAYER_TEAM_SEASONS_FIELDS = [
	"id",
	"season_id",
	"season_name",
	"team_id",
	"team_name",
	"player_id",
	"player_name",
	"games_played",
	"games_started",
	"minutes_total",
	"minutes_per_game",
	"points_total",
	"points_per_game",
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


STAT_INPUT_FIELDS = [
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
	"turnovers",
	"fouls_committed",
	"fouls_received",
	"dunks",
	"plus_minus",
	"efficiency",
]


def as_float(value: str | None) -> float:
	value = clean_text(value).replace(",", ".")

	if not value:
		return 0.0

	try:
		return float(value)
	except ValueError:
		return 0.0


def as_bool(value: str | None) -> bool:
	value = clean_text(value).lower()

	return value in {"1", "true", "sim", "yes", "y"}


def fmt_int(value: float) -> str:
	return str(int(round(value)))


def fmt_float(value: float, digits: int = 2) -> str:
	return f"{value:.{digits}f}"


def fmt_pct(made: float, attempted: float) -> str:
	if attempted <= 0:
		return ""

	return f"{made / attempted:.3f}"


def per_game(total: float, games: int) -> str:
	if games <= 0:
		return "0.00"

	return fmt_float(total / games)


def build_indexes(data_dir: Path) -> tuple[dict[str, dict], dict[str, dict], dict[str, dict]]:
	players = read_csv_dicts(data_dir / "players.csv")
	teams = read_csv_dicts(data_dir / "teams.csv")
	seasons = read_csv_dicts(data_dir / "seasons.csv")

	players_by_id = {
		clean_text(row.get("id")): row
		for row in players
		if clean_text(row.get("id"))
	}

	teams_by_id = {
		clean_text(row.get("id")): row
		for row in teams
		if clean_text(row.get("id"))
	}

	seasons_by_id = {
		clean_text(row.get("id")): row
		for row in seasons
		if clean_text(row.get("id"))
	}

	return players_by_id, teams_by_id, seasons_by_id


def player_display_name(player: dict, fallback: str) -> str:
	return (
		clean_text(player.get("full_name"))
		or clean_text(player.get("display_name"))
		or clean_text(fallback)
	)


def team_display_name(team: dict) -> str:
	return clean_text(team.get("name"))


def season_display_name(season: dict) -> str:
	return clean_text(season.get("name"))


def new_group(
	season_id: str,
	team_id: str,
	player_id: str,
) -> dict:
	row = {
		"season_id": season_id,
		"team_id": team_id,
		"player_id": player_id,
		"_game_ids": set(),
		"_name_counter": Counter(),
		"_games_started": 0,
		"_minutes_total": 0.0,
	}

	for field in STAT_INPUT_FIELDS:
		row[f"_{field}"] = 0.0

	return row


def build_output_row(
	idx: int,
	group: dict,
	players_by_id: dict[str, dict],
	teams_by_id: dict[str, dict],
	seasons_by_id: dict[str, dict],
) -> dict:
	season_id = group["season_id"]
	team_id = group["team_id"]
	player_id = group["player_id"]

	games_played = len(group["_game_ids"])

	fallback_name = ""
	if group["_name_counter"]:
		fallback_name = group["_name_counter"].most_common(1)[0][0]

	player = players_by_id.get(player_id, {})
	team = teams_by_id.get(team_id, {})
	season = seasons_by_id.get(season_id, {})

	fg_made = group["_fg_made"]
	fg_attempted = group["_fg_attempted"]

	three_made = group["_three_made"]
	three_attempted = group["_three_attempted"]

	two_made = group["_two_made"]
	two_attempted = group["_two_attempted"]

	ft_made = group["_ft_made"]
	ft_attempted = group["_ft_attempted"]

	minutes_total = group["_minutes_total"]
	points_total = group["_points"]
	rebounds_total = group["_total_rebounds"]
	assists_total = group["_assists"]
	steals_total = group["_steals"]
	blocks_total = group["_blocks"]
	turnovers_total = group["_turnovers"]
	plus_minus_total = group["_plus_minus"]
	efficiency_total = group["_efficiency"]

	return {
		"id": idx,
		"season_id": season_id,
		"season_name": season_display_name(season),
		"team_id": team_id,
		"team_name": team_display_name(team),
		"player_id": player_id,
		"player_name": player_display_name(player, fallback_name),
		"games_played": games_played,
		"games_started": group["_games_started"],
		"minutes_total": fmt_float(minutes_total),
		"minutes_per_game": per_game(minutes_total, games_played),
		"points_total": fmt_int(points_total),
		"points_per_game": per_game(points_total, games_played),
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
		"offensive_rebounds_total": fmt_int(group["_offensive_rebounds"]),
		"defensive_rebounds_total": fmt_int(group["_defensive_rebounds"]),
		"rebounds_total": fmt_int(rebounds_total),
		"rebounds_per_game": per_game(rebounds_total, games_played),
		"assists_total": fmt_int(assists_total),
		"assists_per_game": per_game(assists_total, games_played),
		"steals_total": fmt_int(steals_total),
		"steals_per_game": per_game(steals_total, games_played),
		"blocks_total": fmt_int(blocks_total),
		"blocks_per_game": per_game(blocks_total, games_played),
		"turnovers_total": fmt_int(turnovers_total),
		"turnovers_per_game": per_game(turnovers_total, games_played),
		"fouls_committed_total": fmt_int(group["_fouls_committed"]),
		"fouls_received_total": fmt_int(group["_fouls_received"]),
		"dunks_total": fmt_int(group["_dunks"]),
		"plus_minus_total": fmt_int(plus_minus_total),
		"plus_minus_per_game": per_game(plus_minus_total, games_played),
		"efficiency_total": fmt_int(efficiency_total),
		"efficiency_per_game": per_game(efficiency_total, games_played),
	}


def build_player_team_seasons(data_dir: Path = DATA_DIR) -> dict:
	player_game_stats = read_csv_dicts(data_dir / "player_game_stats.csv")

	players_by_id, teams_by_id, seasons_by_id = build_indexes(data_dir)

	groups = {}
	skipped = defaultdict(int)

	for row in player_game_stats:
		player_id = clean_text(row.get("player_id"))
		team_id = clean_text(row.get("team_id"))
		season_id = clean_text(row.get("season_id"))
		game_id = clean_text(row.get("game_id"))

		if not player_id:
			skipped["missing_player_id"] += 1
			continue

		if not team_id:
			skipped["missing_team_id"] += 1
			continue

		if not season_id:
			skipped["missing_season_id"] += 1
			continue

		key = (season_id, team_id, player_id)

		if key not in groups:
			groups[key] = new_group(
				season_id=season_id,
				team_id=team_id,
				player_id=player_id,
			)

		group = groups[key]

		if game_id:
			group["_game_ids"].add(game_id)

		name_raw = clean_text(row.get("player_name_raw"))

		if name_raw:
			group["_name_counter"][name_raw] += 1

		if as_bool(row.get("is_starter")):
			group["_games_started"] += 1

		group["_minutes_total"] += as_float(row.get("minutes_decimal"))

		for field in STAT_INPUT_FIELDS:
			group[f"_{field}"] += as_float(row.get(field))

	output_rows = []

	sorted_groups = sorted(
		groups.values(),
		key=lambda group: (
			int(group["season_id"]),
			int(group["team_id"]),
			player_display_name(
				players_by_id.get(group["player_id"], {}),
				group["_name_counter"].most_common(1)[0][0] if group["_name_counter"] else "",
			).lower(),
		),
	)

	for idx, group in enumerate(sorted_groups, start=1):
		output_rows.append(
			build_output_row(
				idx=idx,
				group=group,
				players_by_id=players_by_id,
				teams_by_id=teams_by_id,
				seasons_by_id=seasons_by_id,
			)
		)

	output_path = data_dir / "player_team_seasons.csv"

	write_csv_dicts(
		output_path,
		PLAYER_TEAM_SEASONS_FIELDS,
		output_rows,
	)

	return {
		"output_path": output_path,
		"input_rows": len(player_game_stats),
		"output_rows": len(output_rows),
		"skipped": dict(skipped),
	}