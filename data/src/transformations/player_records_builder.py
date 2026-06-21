from collections import defaultdict
from pathlib import Path

from src.transformations.stats_helpers import as_float, build_indexes, player_name, season_name, sort_int, team_name
from src.utils.csv_io import read_csv_dicts, write_csv_dicts
from src.utils.text import clean_text


DATA_DIR = Path("dados")


PLAYER_RECORDS_FIELDS = [
	"id",
	"player_id",
	"player_name",
	"scope",
	"season_id",
	"season_name",
	"record_type",
	"record_label",
	"value",
	"tie_count",
	"game_id",
	"game_date",
	"team_id",
	"team_name",
	"opponent_team_id",
	"opponent_team_name",
	"home_away",
	"result",
	"team_score",
	"opponent_score",
	"source",
]


RECORD_STATS = [
	("points", "Pontos"),
	("total_rebounds", "Rebotes"),
	("assists", "Assistências"),
	("steals", "Roubos"),
	("blocks", "Tocos"),
	("three_made", "Bolas de 3 convertidas"),
	("efficiency", "Eficiência"),
	("minutes_decimal", "Minutos"),
]


def games_index(games: list[dict]) -> dict[str, dict]:
	return {
		clean_text(row.get("id")): row
		for row in games
		if clean_text(row.get("id"))
	}


def side_and_opponent(row: dict, game: dict) -> tuple[str, str, str, str, str]:
	team_id = clean_text(row.get("team_id"))

	home_team_id = clean_text(game.get("home_team_id"))
	away_team_id = clean_text(game.get("away_team_id"))

	home_score = clean_text(game.get("home_score"))
	away_score = clean_text(game.get("away_score"))

	if team_id == home_team_id:
		return "home", away_team_id, home_score, away_score, game_result(home_score, away_score)

	if team_id == away_team_id:
		return "away", home_team_id, away_score, home_score, game_result(away_score, home_score)

	return "", "", "", "", ""


def game_result(team_score: str, opponent_score: str) -> str:
	try:
		team = int(float(team_score))
		opponent = int(float(opponent_score))
	except ValueError:
		return ""

	if team > opponent:
		return "W"

	if team < opponent:
		return "L"

	return "T"


def format_record_value(record_type: str, value: float) -> str:
	if record_type == "minutes_decimal":
		return f"{value:.2f}"

	return str(int(round(value)))


def choose_best_row(rows: list[dict], record_type: str) -> tuple[dict, float, int]:
	values = [
		(row, as_float(row.get(record_type)))
		for row in rows
	]

	max_value = max(value for _row, value in values)

	tied = [
		row for row, value in values
		if value == max_value
	]

	# Se empatou, escolhe o jogo mais recente só para representar.
	chosen = sorted(
		tied,
		key=lambda row: (
			clean_text(row.get("game_date")),
			sort_int(row.get("game_id")),
		),
		reverse=True,
	)[0]

	return chosen, max_value, len(tied)


def build_record_row(
	idx: int,
	player_id: str,
	scope: str,
	season_id: str,
	record_type: str,
	record_label: str,
	chosen: dict,
	value: float,
	tie_count: int,
	games_by_id: dict[str, dict],
	players_by_id: dict[str, dict],
	teams_by_id: dict[str, dict],
	seasons_by_id: dict[str, dict],
) -> dict:
	game_id = clean_text(chosen.get("game_id"))
	game = games_by_id.get(game_id, {})

	team_id = clean_text(chosen.get("team_id"))

	home_away, opponent_team_id, team_score, opponent_score, result = side_and_opponent(
		chosen,
		game,
	)

	return {
		"id": idx,
		"player_id": player_id,
		"player_name": player_name(players_by_id.get(player_id, {}), clean_text(chosen.get("player_name_raw"))),
		"scope": scope,
		"season_id": season_id,
		"season_name": season_name(seasons_by_id.get(season_id, {})) if season_id else "",
		"record_type": record_type,
		"record_label": record_label,
		"value": format_record_value(record_type, value),
		"tie_count": tie_count,
		"game_id": game_id,
		"game_date": clean_text(game.get("game_date")),
		"team_id": team_id,
		"team_name": team_name(teams_by_id.get(team_id, {})),
		"opponent_team_id": opponent_team_id,
		"opponent_team_name": team_name(teams_by_id.get(opponent_team_id, {})),
		"home_away": home_away,
		"result": result,
		"team_score": team_score,
		"opponent_score": opponent_score,
		"source": "computed_from_player_game_stats",
	}


def build_player_records(data_dir: Path = DATA_DIR) -> dict:
	player_game_stats = read_csv_dicts(data_dir / "player_game_stats.csv")
	games = read_csv_dicts(data_dir / "games.csv")

	players_by_id, teams_by_id, seasons_by_id = build_indexes(data_dir)
	games_by_id = games_index(games)

	valid_rows = [
		row for row in player_game_stats
		if clean_text(row.get("player_id"))
	]

	career_groups = defaultdict(list)
	season_groups = defaultdict(list)

	for row in valid_rows:
		player_id = clean_text(row.get("player_id"))
		season_id = clean_text(row.get("season_id"))

		career_groups[player_id].append(row)

		if season_id:
			season_groups[(player_id, season_id)].append(row)

	output_rows = []
	next_id = 1

	# Recordes de carreira
	for player_id, rows in sorted(career_groups.items(), key=lambda item: sort_int(item[0])):
		for record_type, record_label in RECORD_STATS:
			chosen, value, tie_count = choose_best_row(rows, record_type)

			output_rows.append(
				build_record_row(
					idx=next_id,
					player_id=player_id,
					scope="career",
					season_id="",
					record_type=record_type,
					record_label=record_label,
					chosen=chosen,
					value=value,
					tie_count=tie_count,
					games_by_id=games_by_id,
					players_by_id=players_by_id,
					teams_by_id=teams_by_id,
					seasons_by_id=seasons_by_id,
				)
			)

			next_id += 1

	# Recordes por temporada
	for (player_id, season_id), rows in sorted(
		season_groups.items(),
		key=lambda item: (sort_int(item[0][1]), sort_int(item[0][0])),
	):
		for record_type, record_label in RECORD_STATS:
			chosen, value, tie_count = choose_best_row(rows, record_type)

			output_rows.append(
				build_record_row(
					idx=next_id,
					player_id=player_id,
					scope="season",
					season_id=season_id,
					record_type=record_type,
					record_label=record_label,
					chosen=chosen,
					value=value,
					tie_count=tie_count,
					games_by_id=games_by_id,
					players_by_id=players_by_id,
					teams_by_id=teams_by_id,
					seasons_by_id=seasons_by_id,
				)
			)

			next_id += 1

	output_path = data_dir / "player_records.csv"

	write_csv_dicts(output_path, PLAYER_RECORDS_FIELDS, output_rows)

	return {
		"output_path": output_path,
		"input_rows": len(player_game_stats),
		"valid_rows": len(valid_rows),
		"output_rows": len(output_rows),
	}