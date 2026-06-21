from dataclasses import dataclass
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from src.utils.text import clean_text


BASE_URL = "https://lnb.com.br"


@dataclass
class ParsedGame:
	season_id: int
	competition: str
	game_number: str
	lnb_game_id: str
	game_date: str
	game_time: str
	round: str
	phase: str
	championship: str
	home_team_name: str
	away_team_name: str
	home_team_abbr: str
	away_team_abbr: str
	home_logo_url: str
	away_logo_url: str
	home_score: str
	away_score: str
	status: str
	arena: str
	boxscore_url: str
	source_url: str


def parse_games_from_html(
	html: str,
	season_id: int,
	source_url: str,
	competition: str = "NBB",
) -> list[ParsedGame]:
	"""Extrai jogos da tabela de jogos da LNB."""
	soup = BeautifulSoup(html, "lxml")
	games: list[ParsedGame] = []

	rows = soup.select("table.table_matches_table tbody tr")

	for row in rows:
		game = _parse_game_row(row, season_id, source_url, competition)
		if game:
			games.append(game)

	return _deduplicate(games)


def _parse_game_row(
	row: Tag,
	season_id: int,
	source_url: str,
	competition: str,
) -> ParsedGame | None:
	position_td = row.select_one("td.position_value")
	home_td = row.select_one("td.home_team_value")
	away_td = row.select_one("td.visitor_team_value")

	if not position_td or not home_td or not away_td:
		return None

	game_number = clean_text(position_td.get_text())
	lnb_game_id = clean_text(position_td.get("data-real-id"))

	date_td = row.select_one('td.date_value[data-label="DATA"]')
	game_date, game_time = _extract_date_time(date_td)

	home_team_name = _text_from_selector(row, "td.home_team_value .team-shortname")
	away_team_name = _text_from_selector(row, "td.visitor_team_value .team-shortname")

	home_logo_url = _img_src(row, "td.logo_home_team img")
	away_logo_url = _img_src(row, "td.logo_visitor_team img")

	home_score = _text_from_selector(row, "td.score_value span.home")
	away_score = _text_from_selector(row, "td.score_value span.away")

	boxscore_link = row.select_one("td.score_value a.match_score_relatorio")
	boxscore_url = _abs_url(boxscore_link.get("href")) if boxscore_link else ""

	home_team_abbr, away_team_abbr = _extract_mobile_abbrs(row)

	round_text = clean_text(
		" ".join(
			item.get_text(" ", strip=True)
			for item in row.select("td.game_value span")
		)
	)

	phase = _text_from_selector(row, "td.stage_value")
	championship = _text_from_selector(row, "td.champ_value")
	arena = _text_from_selector(row, "td.gym_value")

	status = "finished" if home_score and away_score else "scheduled"

	return ParsedGame(
		season_id=season_id,
		competition=competition,
		game_number=game_number,
		lnb_game_id=lnb_game_id,
		game_date=game_date,
		game_time=game_time,
		round=round_text,
		phase=phase,
		championship=championship,
		home_team_name=home_team_name,
		away_team_name=away_team_name,
		home_team_abbr=home_team_abbr,
		away_team_abbr=away_team_abbr,
		home_logo_url=home_logo_url,
		away_logo_url=away_logo_url,
		home_score=home_score,
		away_score=away_score,
		status=status,
		arena=arena,
		boxscore_url=boxscore_url,
		source_url=source_url,
	)


def _extract_date_time(date_td: Tag | None) -> tuple[str, str]:
	if not date_td:
		return "", ""

	spans = date_td.find_all("span")
	date = clean_text(spans[0].get_text()) if len(spans) >= 1 else ""
	time = clean_text(spans[1].get_text()) if len(spans) >= 2 else ""

	return date, time


def _extract_mobile_abbrs(row: Tag) -> tuple[str, str]:
	mobile_td = row.select_one("td.matche_for_small")
	if not mobile_td:
		return "", ""

	strongs = mobile_td.find_all("strong")
	if len(strongs) < 2:
		return "", ""

	home_abbr = _clean_abbr(strongs[0].get_text(" ", strip=True))
	away_abbr = _clean_abbr(strongs[-1].get_text(" ", strip=True))

	return home_abbr, away_abbr


def _clean_abbr(value: str) -> str:
	value = clean_text(value)
	pieces = [piece for piece in value.split() if piece.isupper()]

	if pieces:
		return pieces[0]

	return value.replace(" ", "")


def _text_from_selector(row: Tag, selector: str) -> str:
	item = row.select_one(selector)
	return clean_text(item.get_text(" ", strip=True)) if item else ""


def _img_src(row: Tag, selector: str) -> str:
	img = row.select_one(selector)
	return _abs_url(img.get("src")) if img else ""


def _abs_url(url: str | None) -> str:
	if not url:
		return ""
	return urljoin(BASE_URL, url)


def _deduplicate(games: list[ParsedGame]) -> list[ParsedGame]:
	result = []
	seen = set()

	for game in games:
		key = (
			game.season_id,
			game.lnb_game_id or game.game_number,
			game.game_date,
			game.home_team_name,
			game.away_team_name,
		)

		if key in seen:
			continue

		seen.add(key)
		result.append(game)

	return result