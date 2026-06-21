from __future__ import annotations

import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from tqdm import tqdm
from bs4 import BeautifulSoup

from src.scraping.http_client import HttpClient
from src.scraping.parsers.boxscores_parser import (
	NoBoxscoreStatsError,
	ParsedBoxscore,
	ParsedStatLine,
	parse_boxscore_html,
)
from src.utils.csv_io import ensure_csv, next_id, read_csv_dicts, write_csv_dicts
from src.utils.text import clean_text, identity_key


PLAYER_GAME_STATS_FIELDS = [
	"id",
	"game_id",
	"season_id",
	"competition",
	"team_id",
	"opponent_team_id",
	"player_id",
	"player_name_raw",
	"jersey_number",
	"is_starter",
	"minutes_text",
	"minutes_decimal",
	"points",
	"points_attempted",
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
	"offensive_rebounds",
	"defensive_rebounds",
	"total_rebounds",
	"assists",
	"steals",
	"blocks",
	"fouls_committed",
	"fouls_received",
	"turnovers",
	"dunks",
	"plus_minus",
	"efficiency",
	"source_url",
	"parse_model",
	"needs_manual_review",
]

TEAM_GAME_STATS_FIELDS = [
	"id",
	"game_id",
	"season_id",
	"competition",
	"team_id",
	"opponent_team_id",
	"is_home",
	"points",
	"points_attempted",
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
	"offensive_rebounds",
	"defensive_rebounds",
	"total_rebounds",
	"assists",
	"steals",
	"blocks",
	"fouls_committed",
	"fouls_received",
	"turnovers",
	"dunks",
	"plus_minus",
	"efficiency",
	"collective_offensive_rebounds",
	"collective_defensive_rebounds",
	"collective_total_rebounds",
	"source_url",
	"parse_model",
]

FAILED_BOXSCORES_FIELDS = [
	"id",
	"game_id",
	"season_id",
	"boxscore_url",
	"error_type",
	"error_message",
	"last_attempt_at",
]

UNRESOLVED_PLAYERS_FIELDS = [
	"id",
	"game_id",
	"season_id",
	"team_id",
	"team_side",
	"player_name_raw",
	"jersey_number",
	"candidate_player_ids",
	"reason",
	"source_url",
	"created_at",
]

SCRAPE_RUNS_FIELDS = [
	"id",
	"scraper_name",
	"target",
	"started_at",
	"finished_at",
	"status",
	"seasons_requested",
	"seasons_ok",
	"seasons_failed",
	"items_found",
	"items_inserted",
	"items_updated",
	"error_message",
]

RAW_BOXSCORES_FIELDS = [
	"id",
	"scrape_run_id",
	"source_type",
	"season_id",
	"source_url",
	"storage_path",
	"content_sha256",
	"scraped_at",
	"from_cache",
]


def run_scrape_boxscores(
	data_dir: Path,
	workers: int = 2,
	limit: int | None = None,
	force: bool = False,
	strict_players: bool = False,
	only_failed: bool = False,
	cache_only: bool = False,
) -> None:
	"""Popula player_game_stats e team_game_stats a partir dos boxscores."""
	data_dir = Path(data_dir)

	games_path = data_dir / "games.csv"
	players_path = data_dir / "players.csv"
	player_aliases_path = data_dir / "player_aliases.csv"
	team_aliases_path = data_dir / "team_aliases.csv"

	pgs_path = data_dir / "player_game_stats.csv"
	tgs_path = data_dir / "team_game_stats.csv"
	failed_path = data_dir / "_runtime" / "failed_boxscores.csv"
	unresolved_path = data_dir / "_runtime" / "unresolved_boxscore_players.csv"
	runs_path = data_dir / "_runtime" / "scrape_runs.csv"
	raw_path = data_dir / "_runtime" / "raw_boxscores.csv"
	raw_dir = data_dir / "raw" / "boxscores"

	_ensure_outputs(
		pgs_path=pgs_path,
		tgs_path=tgs_path,
		failed_path=failed_path,
		unresolved_path=unresolved_path,
		runs_path=runs_path,
		raw_path=raw_path,
	)

	games = [
		row for row in read_csv_dicts(games_path)
		if clean_text(row.get("boxscore_url"))
	]

	if only_failed:
		failed_ids = {
			clean_text(row.get("game_id"))
			for row in read_csv_dicts(failed_path)
			if clean_text(row.get("game_id"))
		}

		games = [
			row for row in games
			if clean_text(row.get("id")) in failed_ids
		]

	if limit:
		games = games[:limit]

	if not games:
		raise RuntimeError("Nenhum jogo com boxscore_url encontrado em dados/games.csv")

	resolver = PlayerResolver(
		players_rows=read_csv_dicts(players_path),
		player_aliases_rows=read_csv_dicts(player_aliases_path),
		team_aliases_rows=read_csv_dicts(team_aliases_path),
	)

	run_id = _start_run(runs_path, len(games))

	results = []
	failed = []

	max_workers = max(1, min(workers, 3))

	with ThreadPoolExecutor(max_workers=max_workers) as executor:
		futures = [
			executor.submit(
				_process_game,
				game=game,
				raw_dir=raw_dir,
				run_id=run_id,
				force=force,
				cache_only=cache_only,
			)
			for game in games
		]

		for future in tqdm(as_completed(futures), total=len(futures), desc="Boxscores"):
			result = future.result()

			if result["ok"]:
				results.append(result)
			else:
				failed.append(result)

	raw_rows = read_csv_dicts(raw_path)

	for result in results:
		if result.get("raw_row"):
			raw_rows.append(result["raw_row"])

	for result in failed:
		if result.get("raw_row"):
			raw_rows.append(result["raw_row"])

	_fill_raw_ids_and_save(raw_path, raw_rows)

	successful_game_ids = {
		clean_text(result["game"]["id"])
		for result in results
	}

	failed_count = _write_failed_boxscores(
		failed_path=failed_path,
		failed=failed,
		successful_game_ids=successful_game_ids,
	)

	inserted_pgs, updated_pgs, unresolved_count = _merge_player_game_stats(
		pgs_path=pgs_path,
		unresolved_path=unresolved_path,
		results=results,
		resolver=resolver,
		strict_players=strict_players,
	)

	inserted_tgs, updated_tgs = _merge_team_game_stats(
		tgs_path=tgs_path,
		results=results,
	)

	errors = []

	if failed:
		errors.append(f"{len(failed)} boxscores com falha")

	if unresolved_count:
		errors.append(f"{unresolved_count} jogadores não resolvidos")

	_finish_run(
		runs_path=runs_path,
		run_id=run_id,
		status="success" if not errors else "partial",
		seasons_ok=len(results),
		seasons_failed=len(failed),
		items_found=sum(len(r["parsed"].player_stats) for r in results),
		items_inserted=inserted_pgs + inserted_tgs,
		items_updated=updated_pgs + updated_tgs,
		error_message=" | ".join(errors),
	)

	print("\nScraping de boxscores finalizado.")
	print(f"Jogos processados com sucesso: {len(results)}")
	print(f"Boxscores com falha: {failed_count}")
	print(f"Player stats inseridos: {inserted_pgs}")
	print(f"Player stats atualizados: {updated_pgs}")
	print(f"Team stats inseridos: {inserted_tgs}")
	print(f"Team stats atualizados: {updated_tgs}")
	print(f"Jogadores não resolvidos: {unresolved_count}")

	if unresolved_count:
		print("\nVeja dados/_runtime/unresolved_boxscore_players.csv")


def _ensure_outputs(
	pgs_path: Path,
	tgs_path: Path,
	failed_path: Path,
	unresolved_path: Path,
	runs_path: Path,
	raw_path: Path,
) -> None:
	ensure_csv(pgs_path, PLAYER_GAME_STATS_FIELDS)
	ensure_csv(tgs_path, TEAM_GAME_STATS_FIELDS)
	ensure_csv(failed_path, FAILED_BOXSCORES_FIELDS)
	ensure_csv(unresolved_path, UNRESOLVED_PLAYERS_FIELDS)
	ensure_csv(runs_path, SCRAPE_RUNS_FIELDS)
	ensure_csv(raw_path, RAW_BOXSCORES_FIELDS)


def _process_game(
	game: dict,
	raw_dir: Path,
	run_id: int,
	force: bool,
	cache_only: bool = False,
) -> dict:
	game_id = clean_text(game["id"])
	season_id = clean_text(game["season_id"])
	boxscore_url = clean_text(game["boxscore_url"])

	raw_dir.mkdir(parents=True, exist_ok=True)
	html_path = raw_dir / f"game_{game_id}.html"

	from_cache = html_path.exists() and not force
	html = ""

	try:
		if from_cache:
			html = html_path.read_text(encoding="utf-8")
		else:
			if cache_only:
				return _failed_result(
					game=game,
					error_type="cache_missing",
					error_message=f"HTML não encontrado no cache: {html_path}",
				)

			client = HttpClient()
			html = client.get_text(boxscore_url)
			html_path.write_text(html, encoding="utf-8")

		raw_row = {
			"id": "",
			"scrape_run_id": run_id,
			"source_type": "boxscore",
			"season_id": season_id,
			"source_url": boxscore_url,
			"storage_path": str(html_path).replace("\\", "/"),
			"content_sha256": hashlib.sha256(html.encode("utf-8")).hexdigest(),
			"scraped_at": _now(),
			"from_cache": int(from_cache),
		}

		parsed = parse_boxscore_html(html)

		return {
			"ok": True,
			"game": game,
			"parsed": parsed,
			"raw_row": raw_row,
			"error_type": "",
			"error_message": "",
		}

	except NoBoxscoreStatsError as exc:
		error_type = _classify_missing_boxscore(html)

		return _failed_result_with_raw(
			game=game,
			error_type=error_type,
			error_message=str(exc),
			html=html,
			html_path=html_path,
			run_id=run_id,
			from_cache=from_cache,
		)

	except Exception as exc:
		return _failed_result_with_raw(
			game=game,
			error_type="fetch_or_parse_error",
			error_message=str(exc),
			html=html,
			html_path=html_path,
			run_id=run_id,
			from_cache=from_cache,
		)


def _failed_result(game: dict, error_type: str, error_message: str) -> dict:
	return {
		"ok": False,
		"game": game,
		"parsed": None,
		"raw_row": None,
		"error_type": error_type,
		"error_message": error_message,
	}

def _failed_result_with_raw(
	game: dict,
	error_type: str,
	error_message: str,
	html: str,
	html_path: Path,
	run_id: int,
	from_cache: bool,
) -> dict:
	raw_row = None

	if html:
		raw_row = {
			"id": "",
			"scrape_run_id": run_id,
			"source_type": f"boxscore_failed_{error_type}",
			"season_id": clean_text(game.get("season_id")),
			"source_url": clean_text(game.get("boxscore_url")),
			"storage_path": str(html_path).replace("\\", "/"),
			"content_sha256": hashlib.sha256(html.encode("utf-8")).hexdigest(),
			"scraped_at": _now(),
			"from_cache": int(from_cache),
		}

	return {
		"ok": False,
		"game": game,
		"parsed": None,
		"raw_row": raw_row,
		"error_type": error_type,
		"error_message": error_message,
	}

def _classify_missing_boxscore(html: str) -> str:
	"""Classifica páginas sem boxscore parseável."""
	if not html:
		return "empty_html"

	soup = BeautifulSoup(html, "lxml")

	table_count = len(soup.select("table"))
	realtime_tables = soup.select("table.real_time_table_stats[idq='0']")
	classic_tables = soup.select("table.team_general_table[idx='general'], table[idx='general']")

	if "fatal error" in html.lower() or "erro crítico" in html.lower():
		if table_count == 1:
			return "broken_partial_boxscore"
		return "wordpress_fatal_error"

	if len(realtime_tables) >= 2:
		player_rows = sum(_count_real_player_rows(table) for table in realtime_tables)

		if player_rows == 0:
			return "empty_boxscore_template"

		return "unrecognized_realtime_boxscore"

	if len(classic_tables) == 1:
		return "partial_classic_boxscore"

	if len(classic_tables) >= 2:
		return "unrecognized_classic_boxscore"

	if table_count == 0:
		return "no_table_in_page"

	return "unrecognized_table_model"


def _count_real_player_rows(table) -> int:
	count = 0

	for row in table.select("tbody tr, tfoot tr"):
		cells = [
			clean_text(cell.get_text(" ", strip=True))
			for cell in row.find_all(["td", "th"])
		]

		if len(cells) < 5:
			continue

		first = cells[0].replace(" ", "")

		if not first.startswith("#"):
			continue

		name = clean_text(cells[1])

		if not name or name.lower() in {"total", "ações coletivas", "acoes coletivas"}:
			continue

		stats_part = " ".join(cells[2:])

		if any(char.isdigit() for char in stats_part):
			count += 1

	return count


def _merge_player_game_stats(
	pgs_path: Path,
	unresolved_path: Path,
	results: list[dict],
	resolver: "PlayerResolver",
	strict_players: bool,
) -> tuple[int, int, int]:
	rows = read_csv_dicts(pgs_path)
	unresolved_rows = read_csv_dicts(unresolved_path)

	existing = {_pgs_key(row): row for row in rows}
	next_pgs_id = next_id(rows)
	next_unresolved_id = next_id(unresolved_rows)

	inserted = 0
	updated = 0
	unresolved_count = 0
	unresolved_seen = {
		(
			row.get("game_id", ""),
			row.get("team_id", ""),
			identity_key(row.get("player_name_raw", "")),
			row.get("jersey_number", ""),
		)
		for row in unresolved_rows
	}

	for result in tqdm(results, desc="Merge player_game_stats"):
		game = result["game"]
		parsed: ParsedBoxscore = result["parsed"]

		for stat in parsed.player_stats:
			team_id, opponent_team_id = _team_ids_for_side(game, stat.side)
			player_id, candidates, reason = resolver.resolve(
				season_id=clean_text(game["season_id"]),
				team_id=team_id,
				player_name=stat.player_name_raw,
				jersey_number=stat.jersey_number,
			)

			needs_manual_review = 0

			if not player_id:
				unresolved_count += 1
				needs_manual_review = 1

				if strict_players:
					raise RuntimeError(
						f"Jogador não resolvido: game={game['id']} "
						f"team={team_id} #{stat.jersey_number} {stat.player_name_raw}"
					)

				unresolved_key = (
					clean_text(game["id"]),
					team_id,
					identity_key(stat.player_name_raw),
					stat.jersey_number,
				)

				if unresolved_key not in unresolved_seen:
					unresolved_rows.append(
						{
							"id": next_unresolved_id,
							"game_id": clean_text(game["id"]),
							"season_id": clean_text(game["season_id"]),
							"team_id": team_id,
							"team_side": stat.side,
							"player_name_raw": stat.player_name_raw,
							"jersey_number": stat.jersey_number,
							"candidate_player_ids": ",".join(candidates),
							"reason": reason,
							"source_url": clean_text(game.get("boxscore_url")),
							"created_at": _now(),
						}
					)
					unresolved_seen.add(unresolved_key)
					next_unresolved_id += 1

			new_row = _player_stat_row(
				stat=stat,
				game=game,
				team_id=team_id,
				opponent_team_id=opponent_team_id,
				player_id=player_id,
				needs_manual_review=needs_manual_review,
			)

			key = _pgs_key(new_row)

			if key not in existing:
				new_row["id"] = next_pgs_id
				rows.append(new_row)
				existing[key] = new_row
				next_pgs_id += 1
				inserted += 1
			else:
				changed = False
				current = existing[key]

				for field in PLAYER_GAME_STATS_FIELDS:
					if field == "id":
						continue

					if str(current.get(field, "")) != str(new_row.get(field, "")):
						current[field] = new_row.get(field, "")
						changed = True

				if changed:
					updated += 1

	write_csv_dicts(pgs_path, PLAYER_GAME_STATS_FIELDS, sorted(rows, key=lambda row: int(row["id"])))
	write_csv_dicts(unresolved_path, UNRESOLVED_PLAYERS_FIELDS, sorted(unresolved_rows, key=lambda row: int(row["id"])))

	return inserted, updated, unresolved_count


def _merge_team_game_stats(tgs_path: Path, results: list[dict]) -> tuple[int, int]:
	rows = read_csv_dicts(tgs_path)
	existing = {_tgs_key(row): row for row in rows}
	next_tgs_id = next_id(rows)

	inserted = 0
	updated = 0

	for result in tqdm(results, desc="Merge team_game_stats"):
		game = result["game"]
		parsed: ParsedBoxscore = result["parsed"]

		for stat in parsed.team_stats:
			team_id, opponent_team_id = _team_ids_for_side(game, stat.side)
			new_row = _team_stat_row(
				stat=stat,
				game=game,
				team_id=team_id,
				opponent_team_id=opponent_team_id,
			)

			key = _tgs_key(new_row)

			if key not in existing:
				new_row["id"] = next_tgs_id
				rows.append(new_row)
				existing[key] = new_row
				next_tgs_id += 1
				inserted += 1
			else:
				changed = False
				current = existing[key]

				for field in TEAM_GAME_STATS_FIELDS:
					if field == "id":
						continue

					if str(current.get(field, "")) != str(new_row.get(field, "")):
						current[field] = new_row.get(field, "")
						changed = True

				if changed:
					updated += 1

	write_csv_dicts(tgs_path, TEAM_GAME_STATS_FIELDS, sorted(rows, key=lambda row: int(row["id"])))

	return inserted, updated


def _player_stat_row(
	stat: ParsedStatLine,
	game: dict,
	team_id: str,
	opponent_team_id: str,
	player_id: str,
	needs_manual_review: int,
) -> dict:
	return {
		"id": "",
		"game_id": clean_text(game["id"]),
		"season_id": clean_text(game["season_id"]),
		"competition": clean_text(game.get("competition")),
		"team_id": team_id,
		"opponent_team_id": opponent_team_id,
		"player_id": player_id,
		"player_name_raw": stat.player_name_raw,
		"jersey_number": stat.jersey_number,
		"is_starter": stat.is_starter,
		"minutes_text": stat.minutes_text,
		"minutes_decimal": stat.minutes_decimal,
		"points": stat.points,
		"points_attempted": stat.points_attempted,
		"fg_made": stat.fg_made,
		"fg_attempted": stat.fg_attempted,
		"fg_pct": stat.fg_pct,
		"three_made": stat.three_made,
		"three_attempted": stat.three_attempted,
		"three_pct": stat.three_pct,
		"two_made": stat.two_made,
		"two_attempted": stat.two_attempted,
		"two_pct": stat.two_pct,
		"ft_made": stat.ft_made,
		"ft_attempted": stat.ft_attempted,
		"ft_pct": stat.ft_pct,
		"offensive_rebounds": stat.offensive_rebounds,
		"defensive_rebounds": stat.defensive_rebounds,
		"total_rebounds": stat.total_rebounds,
		"assists": stat.assists,
		"steals": stat.steals,
		"blocks": stat.blocks,
		"fouls_committed": stat.fouls_committed,
		"fouls_received": stat.fouls_received,
		"turnovers": stat.turnovers,
		"dunks": stat.dunks,
		"plus_minus": stat.plus_minus,
		"efficiency": stat.efficiency,
		"source_url": clean_text(game.get("boxscore_url")),
		"parse_model": stat.parse_model,
		"needs_manual_review": needs_manual_review,
	}


def _team_stat_row(stat, game: dict, team_id: str, opponent_team_id: str) -> dict:
	return {
		"id": "",
		"game_id": clean_text(game["id"]),
		"season_id": clean_text(game["season_id"]),
		"competition": clean_text(game.get("competition")),
		"team_id": team_id,
		"opponent_team_id": opponent_team_id,
		"is_home": int(stat.side == "home"),
		"points": stat.points,
		"points_attempted": stat.points_attempted,
		"fg_made": stat.fg_made,
		"fg_attempted": stat.fg_attempted,
		"fg_pct": stat.fg_pct,
		"three_made": stat.three_made,
		"three_attempted": stat.three_attempted,
		"three_pct": stat.three_pct,
		"two_made": stat.two_made,
		"two_attempted": stat.two_attempted,
		"two_pct": stat.two_pct,
		"ft_made": stat.ft_made,
		"ft_attempted": stat.ft_attempted,
		"ft_pct": stat.ft_pct,
		"offensive_rebounds": stat.offensive_rebounds,
		"defensive_rebounds": stat.defensive_rebounds,
		"total_rebounds": stat.total_rebounds,
		"assists": stat.assists,
		"steals": stat.steals,
		"blocks": stat.blocks,
		"fouls_committed": stat.fouls_committed,
		"fouls_received": stat.fouls_received,
		"turnovers": stat.turnovers,
		"dunks": stat.dunks,
		"plus_minus": stat.plus_minus,
		"efficiency": stat.efficiency,
		"collective_offensive_rebounds": stat.collective_offensive_rebounds,
		"collective_defensive_rebounds": stat.collective_defensive_rebounds,
		"collective_total_rebounds": stat.collective_total_rebounds,
		"source_url": clean_text(game.get("boxscore_url")),
		"parse_model": stat.parse_model,
	}


def _team_ids_for_side(game: dict, side: str) -> tuple[str, str]:
	if side == "home":
		return clean_text(game.get("home_team_id")), clean_text(game.get("away_team_id"))

	return clean_text(game.get("away_team_id")), clean_text(game.get("home_team_id"))


def _pgs_key(row: dict) -> tuple:
	return (
		clean_text(row.get("game_id")),
		clean_text(row.get("team_id")),
		identity_key(row.get("player_name_raw")),
		clean_text(row.get("jersey_number")),
	)


def _tgs_key(row: dict) -> tuple:
	return (
		clean_text(row.get("game_id")),
		clean_text(row.get("team_id")),
	)


def _write_failed_boxscores(
	failed_path: Path,
	failed: list[dict],
	successful_game_ids: set[str] | None = None,
) -> int:
	rows = read_csv_dicts(failed_path)
	successful_game_ids = successful_game_ids or set()

	rows = [
		row for row in rows
		if clean_text(row.get("game_id")) not in successful_game_ids
	]

	by_game = {clean_text(row["game_id"]): row for row in rows if row.get("game_id")}
	next_failed_id = next_id(rows)

	for item in failed:
		game = item["game"]
		game_id = clean_text(game["id"])

		new_row = {
			"id": "",
			"game_id": game_id,
			"season_id": clean_text(game.get("season_id")),
			"boxscore_url": clean_text(game.get("boxscore_url")),
			"error_type": item["error_type"],
			"error_message": item["error_message"],
			"last_attempt_at": _now(),
		}

		if game_id in by_game:
			by_game[game_id].update({key: value for key, value in new_row.items() if key != "id"})
		else:
			new_row["id"] = next_failed_id
			rows.append(new_row)
			by_game[game_id] = new_row
			next_failed_id += 1

	write_csv_dicts(
		failed_path,
		FAILED_BOXSCORES_FIELDS,
		sorted(rows, key=lambda row: int(row["id"])),
	)

	return len(failed)

def _start_run(runs_path: Path, games_requested: int) -> int:
	runs = read_csv_dicts(runs_path)
	run_id = next_id(runs)

	runs.append(
		{
			"id": run_id,
			"scraper_name": "scrape_boxscores",
			"target": "player_game_stats,team_game_stats",
			"started_at": _now(),
			"finished_at": "",
			"status": "running",
			"seasons_requested": games_requested,
			"seasons_ok": 0,
			"seasons_failed": 0,
			"items_found": 0,
			"items_inserted": 0,
			"items_updated": 0,
			"error_message": "",
		}
	)

	write_csv_dicts(runs_path, SCRAPE_RUNS_FIELDS, runs)
	return run_id


def _finish_run(
	runs_path: Path,
	run_id: int,
	status: str,
	seasons_ok: int,
	seasons_failed: int,
	items_found: int,
	items_inserted: int,
	items_updated: int,
	error_message: str,
) -> None:
	runs = read_csv_dicts(runs_path)

	for row in runs:
		if int(row["id"]) == run_id:
			row["finished_at"] = _now()
			row["status"] = status
			row["seasons_ok"] = seasons_ok
			row["seasons_failed"] = seasons_failed
			row["items_found"] = items_found
			row["items_inserted"] = items_inserted
			row["items_updated"] = items_updated
			row["error_message"] = error_message
			break

	write_csv_dicts(runs_path, SCRAPE_RUNS_FIELDS, runs)


def _fill_raw_ids_and_save(raw_path: Path, raw_rows: list[dict]) -> None:
	raw_next_id = next_id([row for row in raw_rows if row.get("id")])

	for row in raw_rows:
		if not row.get("id"):
			row["id"] = raw_next_id
			raw_next_id += 1

	write_csv_dicts(raw_path, RAW_BOXSCORES_FIELDS, raw_rows)


def _now() -> str:
	return datetime.now().isoformat(timespec="seconds")


class PlayerResolver:
	"""Resolve jogador do boxscore usando temporada + time + nome + camisa."""

	def __init__(
		self,
		players_rows: list[dict],
		player_aliases_rows: list[dict],
		team_aliases_rows: list[dict],
	) -> None:
		self.team_aliases = self._build_team_alias_map(team_aliases_rows)
		self.records = []

		for row in player_aliases_rows:
			player_id = clean_text(row.get("player_id"))
			alias = clean_text(row.get("alias"))

			if not player_id or not alias:
				continue

			season_id = clean_text(row.get("season_id"))
			jersey = clean_text(row.get("jersey_number"))
			team_name_raw = clean_text(row.get("team_name_raw"))
			team_id = self._resolve_team_id(season_id, team_name_raw)

			self.records.append(
				{
					"player_id": player_id,
					"season_id": season_id,
					"name_key": identity_key(alias),
					"jersey_number": jersey,
					"team_id": team_id,
					"source": clean_text(row.get("source")),
				}
			)

		for row in players_rows:
			player_id = clean_text(row.get("id"))
			if not player_id:
				continue

			for alias in [row.get("full_name"), row.get("display_name")]:
				alias = clean_text(alias)
				if not alias:
					continue

				self.records.append(
					{
						"player_id": player_id,
						"season_id": "",
						"name_key": identity_key(alias),
						"jersey_number": "",
						"team_id": "",
						"source": "players",
					}
				)

	def resolve(
		self,
		season_id: str,
		team_id: str,
		player_name: str,
		jersey_number: str,
	) -> tuple[str, list[str], str]:
		name_key = identity_key(player_name)
		jersey_number = clean_text(jersey_number)

		if not name_key:
			return "", [], "empty_player_name"

		candidates = [row for row in self.records if row["name_key"] == name_key]

		if not candidates:
			return "", [], "no_alias_match"

		# Ordem conservadora. Não usa só nome+camisa se houver conflito.
		strategies = [
			lambda r: r["season_id"] == season_id and r["team_id"] == team_id and r["jersey_number"] == jersey_number,
			lambda r: r["season_id"] == season_id and r["team_id"] == team_id and not r["jersey_number"],
			lambda r: r["season_id"] == season_id and r["team_id"] == team_id,
			lambda r: r["season_id"] == season_id and r["jersey_number"] == jersey_number,
			lambda r: r["season_id"] == season_id,
			lambda r: not r["season_id"] and not r["team_id"] and not r["jersey_number"],
		]

		for strategy in strategies:
			matches = [row for row in candidates if strategy(row)]
			player_ids = sorted({row["player_id"] for row in matches})

			if len(player_ids) == 1:
				return player_ids[0], player_ids, "resolved"

			if len(player_ids) > 1:
				return "", player_ids, "ambiguous_match"

		all_ids = sorted({row["player_id"] for row in candidates})
		return "", all_ids, "no_safe_match"

	def _build_team_alias_map(self, rows: list[dict]) -> dict[tuple[str, str], str]:
		result = {}

		for row in rows:
			team_id = clean_text(row.get("team_id"))
			season_id = clean_text(row.get("season_id"))
			alias = clean_text(row.get("alias"))

			if team_id and alias:
				result[(season_id, identity_key(alias))] = team_id
				result[("", identity_key(alias))] = team_id

		return result

	def _resolve_team_id(self, season_id: str, team_name: str) -> str:
		key = identity_key(team_name)

		if not key:
			return ""

		return self.team_aliases.get((season_id, key)) or self.team_aliases.get(("", key), "")
