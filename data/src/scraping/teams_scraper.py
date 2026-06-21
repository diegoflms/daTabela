from __future__ import annotations

import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

from src.scraping.http_client import HttpClient
from src.scraping.parsers.standings_parser import ParsedTeam, parse_teams_from_standings
from src.utils.csv_io import ensure_csv, next_id, read_csv_dicts, write_csv_dicts
from src.utils.text import clean_text, slugify


TEAMS_FIELDS = [
	"id",
	"canonical_name",
	"slug",
	"abbreviation",
	"logo_url",
	"lnb_url",
	"first_seen_season_id",
	"last_seen_season_id",
	"is_active",
]

TEAM_ALIASES_FIELDS = [
	"id",
	"team_id",
	"season_id",
	"alias",
	"alias_type",
	"source",
	"is_primary",
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


def run_scrape_teams(
	data_dir: Path,
	workers: int = 2,
	limit: int | None = None,
	force: bool = False,
) -> None:
	"""Executa scraping de teams e team_aliases."""
	data_dir = Path(data_dir)

	seasons_path = data_dir / "seasons.csv"
	teams_path = data_dir / "teams.csv"
	aliases_path = data_dir / "team_aliases.csv"
	runs_path = data_dir / "_runtime" / "scrape_runs.csv"
	raw_path = data_dir / "_runtime" / "raw_boxscores.csv"
	raw_dir = data_dir / "raw" / "standings"

	_ensure_outputs(teams_path, aliases_path, runs_path, raw_path)

	seasons = read_csv_dicts(seasons_path)
	if limit:
		seasons = seasons[:limit]

	if not seasons:
		raise RuntimeError("Nenhuma temporada encontrada em dados/seasons.csv")

	runs = read_csv_dicts(runs_path)
	run_id = next_id(runs)
	started_at = _now()

	runs.append(
		{
			"id": run_id,
			"scraper_name": "scrape_teams",
			"target": "teams,team_aliases",
			"started_at": started_at,
			"finished_at": "",
			"status": "running",
			"seasons_requested": len(seasons),
			"seasons_ok": 0,
			"seasons_failed": 0,
			"items_found": 0,
			"items_inserted": 0,
			"items_updated": 0,
			"error_message": "",
		}
	)
	write_csv_dicts(runs_path, SCRAPE_RUNS_FIELDS, runs)

	client = HttpClient()
	results = []
	errors = []

	max_workers = max(1, min(workers, 3))

	with ThreadPoolExecutor(max_workers=max_workers) as executor:
		futures = [
			executor.submit(
				_process_season,
				season=season,
				client=client,
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

	raw_rows = read_csv_dicts(raw_path)
	parsed_teams: list[ParsedTeam] = []

	for result in results:
		raw_rows.append(result["raw_row"])
		parsed_teams.extend(result["teams"])

	write_csv_dicts(raw_path, RAW_BOXSCORES_FIELDS, raw_rows)

	inserted, updated = _merge_teams_and_aliases(
		data_dir=data_dir,
		parsed_teams=parsed_teams,
		full_run=limit is None,
	)

	_finish_run(
		runs_path=runs_path,
		run_id=run_id,
		status="partial" if errors else "success",
		seasons_ok=len(results),
		seasons_failed=len(errors),
		items_found=len(parsed_teams),
		items_inserted=inserted,
		items_updated=updated,
		error_message=" | ".join(errors),
	)

	print("\nScraping finalizado.")
	print(f"Temporadas processadas: {len(results)}")
	print(f"Times encontrados: {len(parsed_teams)}")
	print(f"Teams inseridos: {inserted}")
	print(f"Teams atualizados: {updated}")
	print(f"Erros: {len(errors)}")

	if errors:
		print("\nErros parciais:")
		for error in errors:
			print(f"- {error}")


def _ensure_outputs(
	teams_path: Path,
	aliases_path: Path,
	runs_path: Path,
	raw_path: Path,
) -> None:
	ensure_csv(teams_path, TEAMS_FIELDS)
	ensure_csv(aliases_path, TEAM_ALIASES_FIELDS)
	ensure_csv(runs_path, SCRAPE_RUNS_FIELDS)
	ensure_csv(raw_path, RAW_BOXSCORES_FIELDS)


def _process_season(
	season: dict,
	client: HttpClient,
	raw_dir: Path,
	run_id: int,
	force: bool,
) -> dict:
	season_id = int(season["id"])
	season_name = season["name"]

	url_path = season_name_to_url_path(season_name)
	url = f"https://lnb.com.br/nbb/{url_path}"

	raw_dir.mkdir(parents=True, exist_ok=True)
	html_path = raw_dir / f"season_{season_id}_{url_path}.html"

	from_cache = html_path.exists() and not force

	if from_cache:
		html = html_path.read_text(encoding="utf-8")
	else:
		html = client.get_text(url)
		html_path.write_text(html, encoding="utf-8")

	content_hash = hashlib.sha256(html.encode("utf-8")).hexdigest()

	teams = parse_teams_from_standings(html, season_id=season_id)

	return {
		"season_id": season_id,
		"teams": teams,
		"raw_row": {
			"id": "",  # preenchido abaixo
			"scrape_run_id": run_id,
			"source_type": "standings",
			"season_id": season_id,
			"source_url": url,
			"storage_path": str(html_path).replace("\\", "/"),
			"content_sha256": content_hash,
			"scraped_at": _now(),
			"from_cache": int(from_cache),
		},
	}


def _merge_teams_and_aliases(
	data_dir: Path,
	parsed_teams: list[ParsedTeam],
	full_run: bool,
) -> tuple[int, int]:
	teams_path = data_dir / "teams.csv"
	aliases_path = data_dir / "team_aliases.csv"
	raw_path = data_dir / "_runtime" / "raw_boxscores.csv"

	teams_rows = read_csv_dicts(teams_path)
	aliases_rows = read_csv_dicts(aliases_path)
	raw_rows = read_csv_dicts(raw_path)

	# Preenche ids vazios do raw_boxscores.
	raw_next_id = next_id([row for row in raw_rows if row.get("id")])
	for row in raw_rows:
		if not row.get("id"):
			row["id"] = raw_next_id
			raw_next_id += 1
	write_csv_dicts(raw_path, RAW_BOXSCORES_FIELDS, raw_rows)

	team_by_slug = {row["slug"]: row for row in teams_rows if row.get("slug")}

	team_next_id = next_id(teams_rows)
	alias_next_id = next_id(aliases_rows)

	inserted = 0
	updated = 0

	for item in sorted(parsed_teams, key=lambda x: (x.season_id, x.team_slug)):
		team_slug = item.team_slug or slugify(item.season_display_name or item.abbreviation)
		canonical_name = item.season_display_name or item.logo_alt or item.link_text or item.abbreviation

		existing = team_by_slug.get(team_slug)

		if existing is None:
			existing = {
				"id": team_next_id,
				"canonical_name": canonical_name,
				"slug": team_slug,
				"abbreviation": item.abbreviation,
				"logo_url": item.logo_url,
				"lnb_url": item.team_url,
				"first_seen_season_id": item.season_id,
				"last_seen_season_id": item.season_id,
				"is_active": 0,
			}
			teams_rows.append(existing)
			team_by_slug[team_slug] = existing
			team_next_id += 1
			inserted += 1

		else:
			changed = False

			first_seen = min(
				int(existing["first_seen_season_id"]),
				item.season_id,
			)
			last_seen = max(
				int(existing["last_seen_season_id"]),
				item.season_id,
			)

			updates = {
				"canonical_name": canonical_name or existing["canonical_name"],
				"abbreviation": item.abbreviation or existing["abbreviation"],
				"logo_url": item.logo_url or existing["logo_url"],
				"lnb_url": item.team_url or existing["lnb_url"],
				"first_seen_season_id": first_seen,
				"last_seen_season_id": last_seen,
			}

			for key, value in updates.items():
				if str(existing.get(key, "")) != str(value):
					existing[key] = value
					changed = True

			if changed:
				updated += 1

		alias_next_id = _add_aliases(
			aliases_rows=aliases_rows,
			alias_next_id=alias_next_id,
			team_id=int(existing["id"]),
			season_id=item.season_id,
			aliases=item.aliases,
		)

	if full_run and teams_rows:
		max_seen_season = max(int(row["last_seen_season_id"]) for row in teams_rows)
		for row in teams_rows:
			row["is_active"] = int(int(row["last_seen_season_id"]) == max_seen_season)

	teams_rows = sorted(teams_rows, key=lambda row: int(row["id"]))
	aliases_rows = sorted(aliases_rows, key=lambda row: int(row["id"]))

	write_csv_dicts(teams_path, TEAMS_FIELDS, teams_rows)
	write_csv_dicts(aliases_path, TEAM_ALIASES_FIELDS, aliases_rows)

	return inserted, updated


def _add_aliases(
	aliases_rows: list[dict],
	alias_next_id: int,
	team_id: int,
	season_id: int,
	aliases: list[tuple[str, str]],
) -> int:
	existing_keys = {
		(
			int(row["team_id"]),
			int(row["season_id"]),
			clean_text(row["alias"]).lower(),
			row["alias_type"],
		)
		for row in aliases_rows
		if row.get("team_id") and row.get("season_id")
	}

	for alias, alias_type in aliases:
		alias = clean_text(alias)

		if not alias:
			continue

		key = (team_id, season_id, alias.lower(), alias_type)

		if key in existing_keys:
			continue

		aliases_rows.append(
			{
				"id": alias_next_id,
				"team_id": team_id,
				"season_id": season_id,
				"alias": alias,
				"alias_type": alias_type,
				"source": "standings",
				"is_primary": int(alias_type == "season_display_name"),
			}
		)

		existing_keys.add(key)
		alias_next_id += 1

	return alias_next_id


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


def season_name_to_url_path(name: str) -> str:
	"""Converte 2009-10 para 2009-2010."""
	name = clean_text(name)

	if "-" not in name:
		return name

	start_text, end_text = name.split("-", 1)

	start_year = int(start_text)

	if len(end_text) == 2:
		century = start_year // 100 * 100
		end_year = century + int(end_text)

		if end_year < start_year:
			end_year += 100
	else:
		end_year = int(end_text)

	return f"{start_year}-{end_year}"


def _now() -> str:
	return datetime.now().isoformat(timespec="seconds")
