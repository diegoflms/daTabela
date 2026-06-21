from pathlib import Path

from src.utils.csv_io import read_csv_dicts
from src.utils.text import clean_text


DATA_DIR = Path("dados")


PLAYER_TOTAL_FIELDS = [
	"minutes_total",
	"points_total",
	"fg_made",
	"fg_attempted",
	"three_made",
	"three_attempted",
	"two_made",
	"two_attempted",
	"ft_made",
	"ft_attempted",
	"offensive_rebounds_total",
	"defensive_rebounds_total",
	"rebounds_total",
	"assists_total",
	"steals_total",
	"blocks_total",
	"turnovers_total",
	"fouls_committed_total",
	"fouls_received_total",
	"dunks_total",
	"plus_minus_total",
	"efficiency_total",
]


COMMON_STAT_OUTPUT_FIELDS = [
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


def as_float(value: str | None) -> float:
	value = clean_text(value).replace(",", ".")

	if not value:
		return 0.0

	try:
		return float(value)
	except ValueError:
		return 0.0


def as_int(value: str | None) -> int:
	value = clean_text(value)

	if not value:
		return 0

	try:
		return int(float(value.replace(",", ".")))
	except ValueError:
		return 0


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


def sort_int(value: str | int | None) -> int:
	try:
		return int(value or 0)
	except ValueError:
		return 0


def build_indexes(data_dir: Path = DATA_DIR) -> tuple[dict[str, dict], dict[str, dict], dict[str, dict]]:
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


def player_name(player: dict, fallback: str = "") -> str:
	return (
		clean_text(player.get("full_name"))
		or clean_text(player.get("display_name"))
		or clean_text(fallback)
	)


def team_name(team: dict, fallback: str = "") -> str:
	return clean_text(team.get("name")) or clean_text(fallback)


def season_name(season: dict, fallback: str = "") -> str:
	return clean_text(season.get("name")) or clean_text(fallback)


def empty_totals() -> dict[str, float]:
	return {field: 0.0 for field in PLAYER_TOTAL_FIELDS}


def add_totals(target: dict[str, float], row: dict) -> None:
	for field in PLAYER_TOTAL_FIELDS:
		target[field] += as_float(row.get(field))


def stat_output(totals: dict[str, float], games_played: int) -> dict:
	fg_made = totals["fg_made"]
	fg_attempted = totals["fg_attempted"]

	three_made = totals["three_made"]
	three_attempted = totals["three_attempted"]

	two_made = totals["two_made"]
	two_attempted = totals["two_attempted"]

	ft_made = totals["ft_made"]
	ft_attempted = totals["ft_attempted"]

	return {
		"minutes_total": fmt_float(totals["minutes_total"]),
		"minutes_per_game": per_game(totals["minutes_total"], games_played),
		"points_total": fmt_int(totals["points_total"]),
		"points_per_game": per_game(totals["points_total"], games_played),
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