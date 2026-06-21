from __future__ import annotations

import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

from src.scraping.http_client import HttpClient
from src.scraping.parsers.players_parser import (
	ParsedPlayerLink,
	ParsedPlayerProfile,
	parse_player_links_from_stats,
	parse_player_profile,
)
from src.utils.csv_io import ensure_csv, next_id, read_csv_dicts, write_csv_dicts
from src.utils.text import clean_text, identity_key


PLAYERS_FIELDS = [
	"id",
	"full_name",
	"display_name",
	"slug",
	"lnb_url",
	"photo_url",
	"birth_date",
	"position",
	"naturality",
	"height_cm",
	"weight_kg",
	"profile_jersey_number",
	"first_seen_season_id",
	"last_seen_season_id",
	"scrape_status",
	"needs_manual_review",
	"source_url",
]

PLAYER_ALIASES_FIELDS = [
	"id",
	"player_id",
	"season_id",
	"alias",
	"alias_type",
	"jersey_number",
	"team_name_raw",
	"source",
	"is_primary",
]

FAILED_PLAYER_URLS_FIELDS = [
	"id",
	"player_url",
	"player_slug",
	"first_seen_season_id",
	"last_seen_season_id",
	"season_ids",
	"error_type",
	"error_message",
	"last_attempt_at",
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


def run_scrape_players(
	data_dir: Path,
	workers: int = 2,
	limit: int | None = None,
	force: bool = False,
	collect_only: bool = False,
) -> None:
	"""Coleta URLs de jogadores e popula players/player_aliases."""
	data_dir = Path(data_dir)

	seasons_path = data_dir / "seasons.csv"
	players_path = data_dir / "players.csv"
	aliases_path = data_dir / "player_aliases.csv"
	failed_path = data_dir / "_runtime" / "failed_player_urls.csv"
	runs_path = data_dir / "_runtime" / "scrape_runs.csv"
	raw_path = data_dir / "_runtime" / "raw_boxscores.csv"

	stats_raw_dir = data_dir / "raw" / "player_stats_lists"
	players_raw_dir = data_dir / "raw" / "players"

	_ensure_outputs(players_path, aliases_path, failed_path, runs_path, raw_path)

	seasons = read_csv_dicts(seasons_path)
	if limit:
		seasons = seasons[:limit]

	if not seasons:
		raise RuntimeError("Nenhuma temporada encontrada em dados/seasons.csv")

	run_id = _start_run(runs_path, len(seasons))
	errors: list[str] = []

	stats_results = _collect_player_links_by_season(
		seasons=seasons,
		stats_raw_dir=stats_raw_dir,
		run_id=run_id,
		raw_path=raw_path,
		workers=workers,
		force=force,
		errors=errors,
	)

	all_links = []
	for result in stats_results:
		all_links.extend(result)

	unique_links = _merge_link_observations(all_links)

	if collect_only:
		_finish_run(
			runs_path=runs_path,
			run_id=run_id,
			status="success" if not errors else "partial",
			seasons_ok=len(stats_results),
			seasons_failed=len(errors),
			items_found=len(unique_links),
			items_inserted=0,
			items_updated=0,
			error_message=" | ".join(errors),
		)

		print("\nColeta de URLs finalizada.")
		print(f"Jogadores únicos encontrados: {len(unique_links)}")
		print("Nada foi baixado das páginas individuais por causa de --collect-only.")
		return

	profiles, failed_profiles = _collect_profiles(
		unique_links=unique_links,
		players_raw_dir=players_raw_dir,
		run_id=run_id,
		raw_path=raw_path,
		workers=workers,
		force=force,
	)

	inserted, updated = _merge_players_and_aliases(
		players_path=players_path,
		aliases_path=aliases_path,
		links=unique_links,
		profiles=profiles,
		failed_profiles=failed_profiles,
	)

	_write_failed_profiles(
		failed_path=failed_path,
		failed_profiles=failed_profiles,
		links=unique_links,
	)

	if failed_profiles:
		errors.append(f"{len(failed_profiles)} páginas de jogador falharam")

	_finish_run(
		runs_path=runs_path,
		run_id=run_id,
		status="success" if not errors else "partial",
		seasons_ok=len(stats_results),
		seasons_failed=len(errors),
		items_found=len(unique_links),
		items_inserted=inserted,
		items_updated=updated,
		error_message=" | ".join(errors),
	)

	print("\nScraping de players finalizado.")
	print(f"Temporadas processadas: {len(stats_results)}")
	print(f"Jogadores únicos encontrados: {len(unique_links)}")
	print(f"Profiles baixados/parseados: {len(profiles)}")
	print(f"Profiles com falha: {len(failed_profiles)}")
	print(f"Players inseridos: {inserted}")
	print(f"Players atualizados: {updated}")

	if failed_profiles:
		print("\nURLs com falha salvas em dados/_runtime/failed_player_urls.csv")


def _ensure_outputs(
	players_path: Path,
	aliases_path: Path,
	failed_path: Path,
	runs_path: Path,
	raw_path: Path,
) -> None:
	ensure_csv(players_path, PLAYERS_FIELDS)
	ensure_csv(aliases_path, PLAYER_ALIASES_FIELDS)
	ensure_csv(failed_path, FAILED_PLAYER_URLS_FIELDS)
	ensure_csv(runs_path, SCRAPE_RUNS_FIELDS)
	ensure_csv(raw_path, RAW_BOXSCORES_FIELDS)


def _collect_player_links_by_season(
	seasons: list[dict],
	stats_raw_dir: Path,
	run_id: int,
	raw_path: Path,
	workers: int,
	force: bool,
	errors: list[str],
) -> list[list[ParsedPlayerLink]]:
	max_workers = max(1, min(workers, 3))
	results: list[list[ParsedPlayerLink]] = []
	raw_rows = read_csv_dicts(raw_path)

	with ThreadPoolExecutor(max_workers=max_workers) as executor:
		futures = [
			executor.submit(
				_process_stats_season,
				season=season,
				stats_raw_dir=stats_raw_dir,
				run_id=run_id,
				force=force,
			)
			for season in seasons
		]

		for future in tqdm(as_completed(futures), total=len(futures), desc="Listas de jogadores"):
			try:
				result = future.result()
				results.append(result["links"])
				raw_rows.append(result["raw_row"])
			except Exception as exc:
				errors.append(str(exc))

	_fill_raw_ids_and_save(raw_path, raw_rows)
	return results


def _process_stats_season(
	season: dict,
	stats_raw_dir: Path,
	run_id: int,
	force: bool,
) -> dict:
	season_id = int(season["id"])
	season_slug = clean_text(season["slug"])

	source_url = (
		"https://lnb.com.br/nbb/estatisticas/eficiencia/"
		f"?aggr=avg&type=athletes&suffered_rule=0&season%5B%5D={season_slug}"
	)

	stats_raw_dir.mkdir(parents=True, exist_ok=True)
	html_path = stats_raw_dir / f"season_{season_id}_slug_{season_slug}.html"

	from_cache = html_path.exists() and not force

	if from_cache:
		html = html_path.read_text(encoding="utf-8")
	else:
		client = HttpClient()
		html = client.get_text(source_url)
		html_path.write_text(html, encoding="utf-8")

	links = parse_player_links_from_stats(
		html=html,
		season_id=season_id,
		source_url=source_url,
	)

	return {
		"links": links,
		"raw_row": {
			"id": "",
			"scrape_run_id": run_id,
			"source_type": "player_stats_list",
			"season_id": season_id,
			"source_url": source_url,
			"storage_path": str(html_path).replace("\\", "/"),
			"content_sha256": hashlib.sha256(html.encode("utf-8")).hexdigest(),
			"scraped_at": _now(),
			"from_cache": int(from_cache),
		},
	}


def _collect_profiles(
	unique_links: list[dict],
	players_raw_dir: Path,
	run_id: int,
	raw_path: Path,
	workers: int,
	force: bool,
) -> tuple[dict[str, ParsedPlayerProfile], dict[str, str]]:
	profiles: dict[str, ParsedPlayerProfile] = {}
	failed: dict[str, str] = {}

	raw_rows = read_csv_dicts(raw_path)
	max_workers = max(1, min(workers, 3))

	with ThreadPoolExecutor(max_workers=max_workers) as executor:
		futures = [
			executor.submit(
				_process_player_profile,
				link=link,
				players_raw_dir=players_raw_dir,
				run_id=run_id,
				force=force,
			)
			for link in unique_links
		]

		for future in tqdm(as_completed(futures), total=len(futures), desc="Perfis de jogadores"):
			result = future.result()

			raw_row = result.get("raw_row")
			if raw_row:
				raw_rows.append(raw_row)

			if result["ok"]:
				profiles[result["player_slug"]] = result["profile"]
			else:
				failed[result["player_slug"]] = result["error"]

	_fill_raw_ids_and_save(raw_path, raw_rows)
	return profiles, failed


def _process_player_profile(
	link: dict,
	players_raw_dir: Path,
	run_id: int,
	force: bool,
) -> dict:
	player_url = link["player_url"]
	player_slug = link["player_slug"]

	players_raw_dir.mkdir(parents=True, exist_ok=True)
	html_path = players_raw_dir / f"{player_slug}.html"

	from_cache = html_path.exists() and not force

	try:
		if from_cache:
			html = html_path.read_text(encoding="utf-8")
		else:
			client = HttpClient()
			html = client.get_text(player_url)
			html_path.write_text(html, encoding="utf-8")

		profile = parse_player_profile(html=html, player_url=player_url)

		raw_row = {
			"id": "",
			"scrape_run_id": run_id,
			"source_type": "player_profile",
			"season_id": "",
			"source_url": player_url,
			"storage_path": str(html_path).replace("\\", "/"),
			"content_sha256": hashlib.sha256(html.encode("utf-8")).hexdigest(),
			"scraped_at": _now(),
			"from_cache": int(from_cache),
		}

		return {
			"ok": True,
			"player_slug": player_slug,
			"profile": profile,
			"raw_row": raw_row,
			"error": "",
		}

	except Exception as exc:
		return {
			"ok": False,
			"player_slug": player_slug,
			"profile": None,
			"raw_row": None,
			"error": str(exc),
		}


def _merge_link_observations(links: list[ParsedPlayerLink]) -> list[dict]:
	by_slug: dict[str, dict] = {}

	for link in links:
		item = by_slug.setdefault(
			link.player_slug,
			{
				"player_slug": link.player_slug,
				"player_url": link.player_url,
				"first_seen_season_id": link.season_id,
				"last_seen_season_id": link.season_id,
				"season_ids": set(),
				"observations": [],
			},
		)

		item["first_seen_season_id"] = min(item["first_seen_season_id"], link.season_id)
		item["last_seen_season_id"] = max(item["last_seen_season_id"], link.season_id)
		item["season_ids"].add(link.season_id)
		item["observations"].append(link)

	result = []

	for item in by_slug.values():
		item["season_ids"] = sorted(item["season_ids"])
		result.append(item)

	return sorted(result, key=lambda row: row["player_slug"])


def _merge_players_and_aliases(
	players_path: Path,
	aliases_path: Path,
	links: list[dict],
	profiles: dict[str, ParsedPlayerProfile],
	failed_profiles: dict[str, str],
) -> tuple[int, int]:
	players_rows = read_csv_dicts(players_path)
	aliases_rows = read_csv_dicts(aliases_path)

	by_slug = {row["slug"]: row for row in players_rows if row.get("slug")}

	player_next_id = next_id(players_rows)
	inserted = 0
	updated = 0

	for link in tqdm(links, desc="Merge players"):
		slug = link["player_slug"]
		profile = profiles.get(slug)
		failed = slug in failed_profiles

		fallback_obs = link["observations"][0]
		fallback_display_name = fallback_obs.display_name

		new_values = _player_values_from_profile_or_link(
			link=link,
			profile=profile,
			fallback_display_name=fallback_display_name,
			failed=failed,
		)

		existing = by_slug.get(slug)

		if existing is None:
			new_values["id"] = player_next_id
			players_rows.append(new_values)
			by_slug[slug] = new_values
			player_next_id += 1
			inserted += 1
		else:
			changed = False

			for field in PLAYERS_FIELDS:
				if field == "id":
					continue

				new_value = new_values.get(field, "")

				if new_value and str(existing.get(field, "")) != str(new_value):
					existing[field] = new_value
					changed = True

			if changed:
				updated += 1

	alias_next_id = next_id(aliases_rows)
	existing_alias_keys = _build_existing_alias_keys(aliases_rows)

	for link in tqdm(links, desc="Merge aliases"):
		player_row = by_slug[link["player_slug"]]
		player_id = int(player_row["id"])
		profile = profiles.get(link["player_slug"])

		alias_next_id = _add_profile_aliases(
			aliases_rows=aliases_rows,
			existing_alias_keys=existing_alias_keys,
			alias_next_id=alias_next_id,
			player_id=player_id,
			profile=profile,
		)

		alias_next_id = _add_observation_aliases(
			aliases_rows=aliases_rows,
			existing_alias_keys=existing_alias_keys,
			alias_next_id=alias_next_id,
			player_id=player_id,
			observations=link["observations"],
		)

	write_csv_dicts(
		players_path,
		PLAYERS_FIELDS,
		sorted(players_rows, key=lambda row: int(row["id"])),
	)

	write_csv_dicts(
		aliases_path,
		PLAYER_ALIASES_FIELDS,
		sorted(aliases_rows, key=lambda row: int(row["id"])),
	)

	return inserted, updated


def _build_existing_alias_keys(aliases_rows: list[dict]) -> set[tuple]:
	"""Cria índice de aliases já existentes uma vez só."""
	return {
		(
			str(row.get("player_id", "")),
			str(row.get("season_id", "")),
			identity_key(row.get("alias", "")),
			str(row.get("alias_type", "")),
			str(row.get("jersey_number", "")),
			identity_key(row.get("team_name_raw", "")),
		)
		for row in aliases_rows
	}


def _player_values_from_profile_or_link(
	link: dict,
	profile: ParsedPlayerProfile | None,
	fallback_display_name: str,
	failed: bool,
) -> dict:
	if profile:
		return {
			"id": "",
			"full_name": profile.full_name,
			"display_name": profile.display_name or fallback_display_name,
			"slug": link["player_slug"],
			"lnb_url": link["player_url"],
			"photo_url": profile.photo_url,
			"birth_date": profile.birth_date,
			"position": profile.position,
			"naturality": profile.naturality,
			"height_cm": profile.height_cm,
			"weight_kg": profile.weight_kg,
			"profile_jersey_number": profile.profile_jersey_number,
			"first_seen_season_id": link["first_seen_season_id"],
			"last_seen_season_id": link["last_seen_season_id"],
			"scrape_status": "success",
			"needs_manual_review": 0,
			"source_url": link["player_url"],
		}

	return {
		"id": "",
		"full_name": fallback_display_name,
		"display_name": fallback_display_name,
		"slug": link["player_slug"],
		"lnb_url": link["player_url"],
		"photo_url": "",
		"birth_date": "",
		"position": "",
		"naturality": "",
		"height_cm": "",
		"weight_kg": "",
		"profile_jersey_number": "",
		"first_seen_season_id": link["first_seen_season_id"],
		"last_seen_season_id": link["last_seen_season_id"],
		"scrape_status": "failed" if failed else "stats_only",
		"needs_manual_review": int(failed),
		"source_url": link["player_url"],
	}


def _add_profile_aliases(
	aliases_rows: list[dict],
	existing_alias_keys: set[tuple],
	alias_next_id: int,
	player_id: int,
	profile: ParsedPlayerProfile | None,
) -> int:
	if not profile:
		return alias_next_id

	candidates = [
		(profile.full_name, "full_name", 1),
		(profile.display_name, "display_name", 0),
	]

	for alias, alias_type, is_primary in candidates:
		alias_next_id = _add_alias(
			aliases_rows=aliases_rows,
			existing_alias_keys=existing_alias_keys,
			alias_next_id=alias_next_id,
			player_id=player_id,
			season_id="",
			alias=alias,
			alias_type=alias_type,
			jersey_number="",
			team_name_raw="",
			source="player_profile",
			is_primary=is_primary,
		)

	return alias_next_id


def _add_observation_aliases(
	aliases_rows: list[dict],
	existing_alias_keys: set[tuple],
	alias_next_id: int,
	player_id: int,
	observations: list[ParsedPlayerLink],
) -> int:
	for obs in observations:
		alias_next_id = _add_alias(
			aliases_rows=aliases_rows,
			existing_alias_keys=existing_alias_keys,
			alias_next_id=alias_next_id,
			player_id=player_id,
			season_id=obs.season_id,
			alias=obs.display_name,
			alias_type="stats_display_name",
			jersey_number=obs.jersey_number,
			team_name_raw=obs.team_name_raw,
			source="season_stats_efficiency",
			is_primary=0,
		)

	return alias_next_id

def _add_alias(
	aliases_rows: list[dict],
	existing_alias_keys: set[tuple],
	alias_next_id: int,
	player_id: int,
	season_id: int | str,
	alias: str,
	alias_type: str,
	jersey_number: str,
	team_name_raw: str,
	source: str,
	is_primary: int,
) -> int:
	alias = clean_text(alias)

	if not alias:
		return alias_next_id

	key = (
		str(player_id),
		str(season_id),
		identity_key(alias),
		alias_type,
		str(jersey_number),
		identity_key(team_name_raw),
	)

	if key in existing_alias_keys:
		return alias_next_id

	aliases_rows.append(
		{
			"id": alias_next_id,
			"player_id": player_id,
			"season_id": season_id,
			"alias": alias,
			"alias_type": alias_type,
			"jersey_number": jersey_number,
			"team_name_raw": team_name_raw,
			"source": source,
			"is_primary": is_primary,
		}
	)

	existing_alias_keys.add(key)

	return alias_next_id + 1

def _write_failed_profiles(
	failed_path: Path,
	failed_profiles: dict[str, str],
	links: list[dict],
) -> None:
	rows = read_csv_dicts(failed_path)
	by_slug = {row["player_slug"]: row for row in rows if row.get("player_slug")}

	next_failed_id = next_id(rows)

	for link in links:
		slug = link["player_slug"]

		if slug not in failed_profiles:
			continue

		season_ids = ",".join(str(item) for item in link["season_ids"])

		new_row = {
			"id": "",
			"player_url": link["player_url"],
			"player_slug": slug,
			"first_seen_season_id": link["first_seen_season_id"],
			"last_seen_season_id": link["last_seen_season_id"],
			"season_ids": season_ids,
			"error_type": "profile_fetch_or_parse_error",
			"error_message": failed_profiles[slug],
			"last_attempt_at": _now(),
		}

		existing = by_slug.get(slug)

		if existing is None:
			new_row["id"] = next_failed_id
			rows.append(new_row)
			by_slug[slug] = new_row
			next_failed_id += 1
		else:
			existing.update({key: value for key, value in new_row.items() if key != "id"})

	write_csv_dicts(failed_path, FAILED_PLAYER_URLS_FIELDS, sorted(rows, key=lambda row: int(row["id"])))


def _start_run(runs_path: Path, seasons_requested: int) -> int:
	runs = read_csv_dicts(runs_path)
	run_id = next_id(runs)

	runs.append(
		{
			"id": run_id,
			"scraper_name": "scrape_players",
			"target": "players,player_aliases",
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
