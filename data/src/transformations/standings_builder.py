from collections import Counter, defaultdict
from pathlib import Path

from src.utils.csv_io import read_csv_dicts, write_csv_dicts
from src.utils.text import clean_text, remove_accents


DATA_DIR = Path("dados")


STANDINGS_FIELDS = [
	"id",
	"season_id",
	"season_name",
	"competition",
	"rank",
	"team_id",
	"team_name",
	"team_abbr",
	"ap_pct",
	"games_played",
	"wins",
	"losses",
	"home_record",
	"away_record",
	"home_wins",
	"home_losses",
	"away_wins",
	"away_losses",
	"points_for",
	"points_against",
	"point_diff",
	"qualified_playoffs",
	"finish_stage",
	"finish_stage_order",
	"is_champion",
	"source",
]


POSTSEASON_STAGE_ORDER = {
	"nao_classificou": 0,
	"playoffs": 1,
	"oitavas": 2,
	"quartas": 3,
	"semifinal": 4,
	"vice_campeao": 5,
	"campeao": 6,
}


POSTSEASON_STAGE_LABEL = {
	"nao_classificou": "não classificou",
	"playoffs": "playoffs",
	"oitavas": "oitavas",
	"quartas": "quartas",
	"semifinal": "semifinal",
	"vice_campeao": "vice-campeão",
	"campeao": "campeão",
}


def norm(value: str | None) -> str:
	value = clean_text(value).lower()
	value = remove_accents(value)
	return value


def as_int(value: str | None) -> int | None:
	value = clean_text(value)

	if not value:
		return None

	try:
		return int(float(value.replace(",", ".")))
	except ValueError:
		return None


def as_bool(value: str | None) -> bool:
	return clean_text(value).lower() in {"1", "true", "sim", "yes", "y"}


def valid_finished_game(row: dict) -> bool:
	home_team_id = clean_text(row.get("home_team_id"))
	away_team_id = clean_text(row.get("away_team_id"))
	home_score = as_int(row.get("home_score"))
	away_score = as_int(row.get("away_score"))

	if not home_team_id or not away_team_id:
		return False

	if home_score is None or away_score is None:
		return False

	return True


def stage_from_game(row: dict) -> str:
	text = " ".join(
		[
			norm(row.get("phase")),
			norm(row.get("round")),
		]
	)

	if not text.strip():
		return ""

	# Mais específico primeiro.
	if "final" in text and "semi" not in text and "quarta" not in text and "oitava" not in text:
		return "final"

	if "semi" in text:
		return "semifinal"

	if "quarta" in text or "quartas" in text:
		return "quartas"

	if "oitava" in text or "oitavas" in text:
		return "oitavas"

	if "playoff" in text or "mata mata" in text or "mata-mata" in text:
		return "playoffs"

	return ""


def is_postseason_game(row: dict) -> bool:
	return bool(stage_from_game(row))


def is_regular_season_game(row: dict) -> bool:
	return valid_finished_game(row) and not is_postseason_game(row)


def get_winner_team_id(row: dict) -> str:
	winner = clean_text(row.get("winner_team_id"))

	if winner:
		return winner

	home_score = as_int(row.get("home_score"))
	away_score = as_int(row.get("away_score"))

	if home_score is None or away_score is None:
		return ""

	if home_score > away_score:
		return clean_text(row.get("home_team_id"))

	if away_score > home_score:
		return clean_text(row.get("away_team_id"))

	return ""


def new_team_row(season_id: str, competition: str, team_id: str) -> dict:
	return {
		"season_id": season_id,
		"competition": competition,
		"team_id": team_id,
		"games_played": 0,
		"wins": 0,
		"losses": 0,
		"home_wins": 0,
		"home_losses": 0,
		"away_wins": 0,
		"away_losses": 0,
		"points_for": 0,
		"points_against": 0,
		"_abbr_counter": Counter(),
	}


def update_regular_season_row(
	table: dict,
	season_id: str,
	competition: str,
	team_id: str,
	team_abbr: str,
	points_for: int,
	points_against: int,
	is_home: bool,
) -> None:
	key = (season_id, competition, team_id)

	if key not in table:
		table[key] = new_team_row(
			season_id=season_id,
			competition=competition,
			team_id=team_id,
		)

	row = table[key]

	row["games_played"] += 1
	row["points_for"] += points_for
	row["points_against"] += points_against

	if team_abbr:
		row["_abbr_counter"][team_abbr] += 1

	won = points_for > points_against

	if won:
		row["wins"] += 1

		if is_home:
			row["home_wins"] += 1
		else:
			row["away_wins"] += 1
	else:
		row["losses"] += 1

		if is_home:
			row["home_losses"] += 1
		else:
			row["away_losses"] += 1


def build_regular_season_table(games: list[dict]) -> dict:
	table = {}

	for game in games:
		if not is_regular_season_game(game):
			continue

		season_id = clean_text(game.get("season_id"))
		competition = clean_text(game.get("competition")) or "NBB"

		home_team_id = clean_text(game.get("home_team_id"))
		away_team_id = clean_text(game.get("away_team_id"))

		home_score = as_int(game.get("home_score"))
		away_score = as_int(game.get("away_score"))

		if not season_id or not home_team_id or not away_team_id:
			continue

		if home_score is None or away_score is None:
			continue

		update_regular_season_row(
			table=table,
			season_id=season_id,
			competition=competition,
			team_id=home_team_id,
			team_abbr=clean_text(game.get("home_team_abbr_raw")),
			points_for=home_score,
			points_against=away_score,
			is_home=True,
		)

		update_regular_season_row(
			table=table,
			season_id=season_id,
			competition=competition,
			team_id=away_team_id,
			team_abbr=clean_text(game.get("away_team_abbr_raw")),
			points_for=away_score,
			points_against=home_score,
			is_home=False,
		)

	return table


def build_postseason_finish(games: list[dict], seasons_by_id: dict[str, dict]) -> dict[tuple[str, str], str]:
	"""
	Retorna:
	(season_id, team_id) -> finish_stage_key
	"""
	team_stage = defaultdict(lambda: "nao_classificou")
	final_wins = defaultdict(Counter)
	final_teams = defaultdict(set)

	for game in games:
		if not valid_finished_game(game):
			continue

		season_id = clean_text(game.get("season_id"))
		home_team_id = clean_text(game.get("home_team_id"))
		away_team_id = clean_text(game.get("away_team_id"))

		if not season_id or not home_team_id or not away_team_id:
			continue

		stage = stage_from_game(game)

		if not stage:
			continue

		if stage == "final":
			stage_key = "vice_campeao"
		else:
			stage_key = stage

		for team_id in [home_team_id, away_team_id]:
			key = (season_id, team_id)

			old_stage = team_stage[key]

			if POSTSEASON_STAGE_ORDER[stage_key] > POSTSEASON_STAGE_ORDER[old_stage]:
				team_stage[key] = stage_key

		if stage == "final":
			winner = get_winner_team_id(game)

			final_teams[season_id].add(home_team_id)
			final_teams[season_id].add(away_team_id)

			if winner:
				final_wins[season_id][winner] += 1

	for season_id, wins_counter in final_wins.items():
		if not wins_counter:
			continue

		champion_id, champion_wins = wins_counter.most_common(1)[0]

		# Se tiver empate em vitórias na final, não crava campeão.
		tied = [
			team_id for team_id, wins in wins_counter.items()
			if wins == champion_wins
		]

		if len(tied) == 1:
			team_stage[(season_id, champion_id)] = "campeao"

			for team_id in final_teams.get(season_id, set()):
				if team_id != champion_id:
					team_stage[(season_id, team_id)] = "vice_campeao"

	# Temporada atual sem playoff finalizado: evita marcar todo mundo como "não classificou".
	for season_id, season in seasons_by_id.items():
		if not as_bool(season.get("is_current")):
			continue

		season_has_postseason = any(
			key_season == season_id and stage != "nao_classificou"
			for (key_season, _team_id), stage in team_stage.items()
		)

		if not season_has_postseason:
			continue

	return dict(team_stage)


def team_name(team: dict) -> str:
	return clean_text(team.get("name"))


def season_name(season: dict) -> str:
	return clean_text(season.get("name"))


def format_pct(wins: int, games_played: int) -> str:
	if games_played <= 0:
		return "0.0"

	return f"{(wins / games_played) * 100:.1f}"


def format_record(wins: int, losses: int) -> str:
	return f"{wins}-{losses}"


def finish_stage_for_team(
	season_id: str,
	team_id: str,
	postseason_finish: dict[tuple[str, str], str],
	seasons_by_id: dict[str, dict],
) -> str:
	season = seasons_by_id.get(season_id, {})

	if as_bool(season.get("is_current")):
		# Se já tiver stage, mostra. Se não, temporada está em andamento.
		stage_key = postseason_finish.get((season_id, team_id))

		if not stage_key:
			return "em andamento"

		return POSTSEASON_STAGE_LABEL.get(stage_key, stage_key)

	stage_key = postseason_finish.get((season_id, team_id), "nao_classificou")
	return POSTSEASON_STAGE_LABEL.get(stage_key, stage_key)


def finish_stage_order_for_label(label: str) -> int:
	for key, value in POSTSEASON_STAGE_LABEL.items():
		if value == label:
			return POSTSEASON_STAGE_ORDER[key]

	if label == "em andamento":
		return -1

	return 0


def build_standings(data_dir: Path = DATA_DIR) -> dict:
	games = read_csv_dicts(data_dir / "games.csv")
	teams = read_csv_dicts(data_dir / "teams.csv")
	seasons = read_csv_dicts(data_dir / "seasons.csv")

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

	regular_table = build_regular_season_table(games)
	postseason_finish = build_postseason_finish(games, seasons_by_id)

	by_season_competition = defaultdict(list)

	for row in regular_table.values():
		by_season_competition[(row["season_id"], row["competition"])].append(row)

	output_rows = []
	next_id = 1

	for (season_id, competition), rows in sorted(
		by_season_competition.items(),
		key=lambda item: (int(item[0][0]), item[0][1]),
	):
		ranked = sorted(
			rows,
			key=lambda row: (
				-(row["wins"] / row["games_played"] if row["games_played"] else 0),
				-row["wins"],
				-(row["points_for"] - row["points_against"]),
				-row["points_for"],
				team_name(teams_by_id.get(row["team_id"], {})),
			),
		)

		for rank, row in enumerate(ranked, start=1):
			team_id = row["team_id"]
			team = teams_by_id.get(team_id, {})
			season = seasons_by_id.get(season_id, {})

			point_diff = row["points_for"] - row["points_against"]

			if row["_abbr_counter"]:
				abbr = row["_abbr_counter"].most_common(1)[0][0]
			else:
				abbr = clean_text(team.get("abbr")) or clean_text(team.get("short_name"))

			finish_stage = finish_stage_for_team(
				season_id=season_id,
				team_id=team_id,
				postseason_finish=postseason_finish,
				seasons_by_id=seasons_by_id,
			)

			qualified_playoffs = finish_stage not in {
				"não classificou",
				"em andamento",
			}

			is_champion = finish_stage == "campeão"

			output_rows.append(
				{
					"id": next_id,
					"season_id": season_id,
					"season_name": season_name(season),
					"competition": competition,
					"rank": rank,
					"team_id": team_id,
					"team_name": team_name(team),
					"team_abbr": abbr,
					"ap_pct": format_pct(row["wins"], row["games_played"]),
					"games_played": row["games_played"],
					"wins": row["wins"],
					"losses": row["losses"],
					"home_record": format_record(row["home_wins"], row["home_losses"]),
					"away_record": format_record(row["away_wins"], row["away_losses"]),
					"home_wins": row["home_wins"],
					"home_losses": row["home_losses"],
					"away_wins": row["away_wins"],
					"away_losses": row["away_losses"],
					"points_for": row["points_for"],
					"points_against": row["points_against"],
					"point_diff": point_diff,
					"qualified_playoffs": int(qualified_playoffs),
					"finish_stage": finish_stage,
					"finish_stage_order": finish_stage_order_for_label(finish_stage),
					"is_champion": int(is_champion),
					"source": "computed_from_games",
				}
			)

			next_id += 1

	output_path = data_dir / "standings.csv"

	write_csv_dicts(
		output_path,
		STANDINGS_FIELDS,
		output_rows,
	)

	return {
		"output_path": output_path,
		"games_read": len(games),
		"standings_rows": len(output_rows),
		"regular_games": sum(1 for game in games if is_regular_season_game(game)),
		"postseason_games": sum(1 for game in games if valid_finished_game(game) and is_postseason_game(game)),
	}