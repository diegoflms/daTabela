from __future__ import annotations

import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

from src.scraping.http_client import HttpClient
from src.scraping.parsers.games_parser import ParsedGame, parse_games_from_html
from src.utils.csv_io import ensure_csv, next_id, read_csv_dicts, write_csv_dicts
from src.utils.text import clean_text, remove_accents, slugify


GAMES_FIELDS = [
	"id",
	"season_id",
	"competition",
	"game_number",
	"lnb_game_id",
	"game_date",
	"game_time",
	"round",
	"phase",
	"home_team_id",
	"away_team_id",
	"home_team_name_raw",
	"away_team_name_raw",
	"home_team_abbr_raw",
	"away_team_abbr_raw",
	"home_score",
	"away_score",
	"winner_team_id",
	"status",
	"arena",
	"championship",
	"boxscore_url",
	"source_url",
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


def run_scrape_games(
	data_dir: Path,
	workers: int = 2,
	limit: int | None = None,
	force: bool = False,
	strict_teams: bool = False,
) -> None:
	"""Executa scraping de games.csv."""
	data_dir = Path(data_dir)

	seasons_path = data_dir / "seasons.csv"
	teams_path = data_dir / "teams.csv"
	aliases_path = data_dir / "team_aliases.csv"
	games_path = data_dir / "games.csv"
	runs_path = data_dir / "_runtime" / "scrape_runs.csv"
	raw_path = data_dir / "_runtime" / "raw_boxscores.csv"
	raw_dir = data_dir / "raw" / "games"

	_ensure_outputs(games_path, runs_path, raw_path)

	seasons = read_csv_dicts(seasons_path)
	if limit:
		seasons = seasons[:limit]

	if not seasons:
		raise RuntimeError("Nenhuma temporada encontrada em dados/seasons.csv")

	team_resolver = TeamResolver(
		teams_rows=read_csv_dicts(teams_path),
		aliases_rows=read_csv_dicts(aliases_path),
	)

	run_id = _start_run(runs_path, len(seasons))

	results = []
	errors = []

	max_workers = max(1, min(workers, 3))

	with ThreadPoolExecutor(max_workers=max_workers) as executor:
		futures = [
			executor.submit(
				_process_season,
				season=season,
				raw_dir=raw_dir,
				run_id=run_id,
				force=force,
			)
			for season in seasons
		]

		for future in tqdm(as_completed(futures), total=len(futures), desc="Temporadas"):
			try:
				results.append(future.result())
			except Exception as exc:
				errors.append(str(exc))

	parsed_games: list[ParsedGame] = []
	raw_rows = read_csv_dicts(raw_path)

	for result in results:
		parsed_games.extend(result["games"])
		raw_rows.append(result["raw_row"])

	_fill_raw_ids_and_save(raw_path, raw_rows)

	inserted, updated, unresolved = _merge_games(
		games_path=games_path,
		parsed_games=parsed_games,
		team_resolver=team_resolver,
		strict_teams=strict_teams,
	)

	if unresolved:
		errors.append(
			"Times não resolvidos: "
			+ "; ".join(sorted(unresolved)[:30])
			+ (" ..." if len(unresolved) > 30 else "")
		)

	_finish_run(
		runs_path=runs_path,
		run_id=run_id,
		status="partial" if errors else "success",
		seasons_ok=len(results),
		seasons_failed=len(errors),
		items_found=len(parsed_games),
		items_inserted=inserted,
		items_updated=updated,
		error_message=" | ".join(errors),
	)

	print("\nScraping de games finalizado.")
	print(f"Temporadas processadas: {len(results)}")
	print(f"Jogos encontrados: {len(parsed_games)}")
	print(f"Games inseridos: {inserted}")
	print(f"Games atualizados: {updated}")
	print(f"Times não resolvidos: {len(unresolved)}")
	print(f"Erros: {len(errors)}")

	if unresolved:
		print("\nAmostra de times não resolvidos:")
		for item in sorted(unresolved)[:20]:
			print(f"- {item}")


def _ensure_outputs(games_path: Path, runs_path: Path, raw_path: Path) -> None:
	ensure_csv(games_path, GAMES_FIELDS)
	ensure_csv(runs_path, SCRAPE_RUNS_FIELDS)
	ensure_csv(raw_path, RAW_BOXSCORES_FIELDS)


def _process_season(
	season: dict,
	raw_dir: Path,
	run_id: int,
	force: bool,
) -> dict:
	season_id = int(season["id"])
	season_slug = clean_text(season["slug"])

	source_url = f"https://lnb.com.br/nbb/tabela-de-jogos/?season%5B%5D={season_slug}"

	raw_dir.mkdir(parents=True, exist_ok=True)
	html_path = raw_dir / f"season_{season_id}_slug_{season_slug}.html"

	from_cache = html_path.exists() and not force

	if from_cache:
		html = html_path.read_text(encoding="utf-8")
	else:
		client = HttpClient()
		html = client.get_text(source_url)
		html_path.write_text(html, encoding="utf-8")

	content_hash = hashlib.sha256(html.encode("utf-8")).hexdigest()

	games = parse_games_from_html(
		html=html,
		season_id=season_id,
		source_url=source_url,
		competition="NBB",
	)

	return {
		"season_id": season_id,
		"games": games,
		"raw_row": {
			"id": "",
			"scrape_run_id": run_id,
			"source_type": "games_list",
			"season_id": season_id,
			"source_url": source_url,
			"storage_path": str(html_path).replace("\\", "/"),
			"content_sha256": content_hash,
			"scraped_at": _now(),
			"from_cache": int(from_cache),
		},
	}


def _merge_games(
	games_path: Path,
	parsed_games: list[ParsedGame],
	team_resolver: "TeamResolver",
	strict_teams: bool,
) -> tuple[int, int, set[str]]:
	games_rows = read_csv_dicts(games_path)
	game_next_id = next_id(games_rows)

	existing_by_key = {
		_game_key_from_row(row): row
		for row in games_rows
		if _game_key_from_row(row)
	}

	inserted = 0
	updated = 0
	unresolved: set[str] = set()

	for game in sorted(parsed_games, key=lambda item: (item.season_id, item.game_date, item.game_time, item.game_number)):
		home_team_id = team_resolver.resolve(
			season_id=game.season_id,
			name=game.home_team_name,
			abbr=game.home_team_abbr,
		)

		away_team_id = team_resolver.resolve(
			season_id=game.season_id,
			name=game.away_team_name,
			abbr=game.away_team_abbr,
		)

		if not home_team_id:
			unresolved.add(f"season_id={game.season_id} home={game.home_team_name}/{game.home_team_abbr}")

		if not away_team_id:
			unresolved.add(f"season_id={game.season_id} away={game.away_team_name}/{game.away_team_abbr}")

		if strict_teams and (not home_team_id or not away_team_id):
			raise RuntimeError("Existem times não resolvidos. Rode sem --strict-teams para gerar CSV parcial.")

		winner_team_id = _winner_team_id(
			home_team_id=home_team_id,
			away_team_id=away_team_id,
			home_score=game.home_score,
			away_score=game.away_score,
		)

		new_row = {
			"id": "",
			"season_id": game.season_id,
			"competition": game.competition,
			"game_number": game.game_number,
			"lnb_game_id": game.lnb_game_id,
			"game_date": _to_iso_date(game.game_date),
			"game_time": game.game_time,
			"round": game.round,
			"phase": game.phase,
			"home_team_id": home_team_id,
			"away_team_id": away_team_id,
			"home_team_name_raw": game.home_team_name,
			"away_team_name_raw": game.away_team_name,
			"home_team_abbr_raw": game.home_team_abbr,
			"away_team_abbr_raw": game.away_team_abbr,
			"home_score": game.home_score,
			"away_score": game.away_score,
			"winner_team_id": winner_team_id,
			"status": game.status,
			"arena": game.arena,
			"championship": game.championship,
			"boxscore_url": game.boxscore_url,
			"source_url": game.source_url,
		}

		key = _game_key_from_values(new_row)

		existing = existing_by_key.get(key)

		if existing is None:
			new_row["id"] = game_next_id
			games_rows.append(new_row)
			existing_by_key[key] = new_row
			game_next_id += 1
			inserted += 1
		else:
			changed = False

			for field in GAMES_FIELDS:
				if field == "id":
					continue

				if str(existing.get(field, "")) != str(new_row.get(field, "")):
					existing[field] = new_row.get(field, "")
					changed = True

			if changed:
				updated += 1

	games_rows = sorted(games_rows, key=lambda row: int(row["id"]))
	write_csv_dicts(games_path, GAMES_FIELDS, games_rows)

	return inserted, updated, unresolved


def _game_key_from_row(row: dict) -> tuple:
	if row.get("lnb_game_id"):
		return ("lnb_game_id", row["lnb_game_id"])

	return _game_key_from_values(row)


def _game_key_from_values(row: dict) -> tuple:
	if row.get("lnb_game_id"):
		return ("lnb_game_id", row["lnb_game_id"])

	return (
		"fallback",
		row.get("season_id", ""),
		row.get("game_date", ""),
		row.get("game_time", ""),
		row.get("home_team_id", ""),
		row.get("away_team_id", ""),
		row.get("home_team_name_raw", ""),
		row.get("away_team_name_raw", ""),
	)


def _winner_team_id(
	home_team_id: str,
	away_team_id: str,
	home_score: str,
	away_score: str,
) -> str:
	try:
		home = int(home_score)
		away = int(away_score)
	except ValueError:
		return ""

	if home > away:
		return home_team_id

	if away > home:
		return away_team_id

	return ""


def _to_iso_date(value: str) -> str:
	value = clean_text(value)

	if not value:
		return ""

	try:
		day, month, year = value.split("/")
		return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
	except ValueError:
		return value


def _start_run(runs_path: Path, seasons_requested: int) -> int:
	runs = read_csv_dicts(runs_path)
	run_id = next_id(runs)

	runs.append(
		{
			"id": run_id,
			"scraper_name": "scrape_games",
			"target": "games",
			"started_at": _now(),
			"finished_at": "",
			"status": "running",
			"seasons_requested": seasons_requested,
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


class TeamResolver:
	"""Resolve nomes/siglas do HTML para team_id."""

	def __init__(self, teams_rows: list[dict], aliases_rows: list[dict]) -> None:
		self.by_season: dict[int, dict[str, str]] = {}
		self.global_map: dict[str, str] = {}

		for row in aliases_rows:
			team_id = clean_text(row.get("team_id"))
			season_id_text = clean_text(row.get("season_id"))
			alias = clean_text(row.get("alias"))

			if not team_id or not season_id_text or not alias:
				continue

			try:
				season_id = int(season_id_text)
			except ValueError:
				continue

			self.by_season.setdefault(season_id, {})[_key(alias)] = team_id

		for row in teams_rows:
			team_id = clean_text(row.get("id"))
			if not team_id:
				continue

			for value in [
				row.get("canonical_name"),
				row.get("abbreviation"),
				row.get("slug"),
			]:
				value = clean_text(value)
				if value:
					self.global_map[_key(value)] = team_id
					self.global_map[_key(slugify(value))] = team_id

	def resolve(self, season_id: int, name: str, abbr: str = "") -> str:
		candidates = [name, abbr, slugify(name)]

		season_map = self.by_season.get(season_id, {})

		for candidate in candidates:
			key = _key(candidate)
			if key in season_map:
				return season_map[key]

		for candidate in candidates:
			key = _key(candidate)
			if key in self.global_map:
				return self.global_map[key]

		return ""


def _key(value: str) -> str:
	value = remove_accents(clean_text(value).lower())
	return "".join(ch for ch in value if ch.isalnum())
