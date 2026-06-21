from dataclasses import dataclass
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from src.utils.text import (
	clean_text,
	extract_team_slug_from_url,
	image_key,
	slugify,
	title_from_slug,
)


BASE_URL = "https://lnb.com.br"


@dataclass
class ParsedTeam:
	season_id: int
	abbreviation: str
	season_display_name: str
	logo_url: str
	logo_alt: str
	team_url: str
	team_slug: str
	link_text: str
	aliases: list[tuple[str, str]]


def parse_teams_from_standings(html: str, season_id: int) -> list[ParsedTeam]:
	"""Extrai times e aliases da página de standings."""
	soup = BeautifulSoup(html, "lxml")
	parsed: list[ParsedTeam] = []

	for team_node in soup.select(".team_first"):
		row = team_node.find_parent("tr")
		if not row:
			continue

		abbreviation = clean_text(team_node.get_text())
		if not abbreviation or len(abbreviation) > 12:
			continue

		logo_img = row.select_one(".logo img") or row.find("img")
		logo_url = _abs_url(logo_img.get("src")) if logo_img else ""
		logo_alt = clean_text(logo_img.get("alt")) if logo_img else ""

		detail_row = _next_detail_row(row)
		team_url = _find_team_url(row) or _find_team_url(detail_row)
		team_slug = extract_team_slug_from_url(team_url)

		link_text = _find_team_link_text(row) or _find_team_link_text(detail_row)
		season_display_name = _find_name_from_game_block(detail_row, logo_url)

		fallback_name = (
			season_display_name
			or logo_alt
			or link_text
			or title_from_slug(team_slug)
			or abbreviation
		)

		aliases = _build_aliases(
			abbreviation=abbreviation,
			season_display_name=season_display_name or fallback_name,
			logo_alt=logo_alt,
			link_text=link_text,
			team_slug=team_slug,
		)

		parsed.append(
			ParsedTeam(
				season_id=season_id,
				abbreviation=abbreviation,
				season_display_name=season_display_name or fallback_name,
				logo_url=logo_url,
				logo_alt=logo_alt,
				team_url=team_url,
				team_slug=team_slug or slugify(fallback_name),
				link_text=link_text,
				aliases=aliases,
			)
		)

	return _deduplicate(parsed)


def _abs_url(url: str | None) -> str:
	if not url:
		return ""
	return urljoin(BASE_URL, url)


def _next_detail_row(row: Tag) -> Tag | None:
	"""Pega a próxima linha HTML útil após a linha do time."""
	current = row

	for _ in range(4):
		current = current.find_next_sibling()
		if isinstance(current, Tag):
			return current

	return None


def _find_team_url(context: Tag | None) -> str:
	if not context:
		return ""

	link = context.select_one('a[href*="/equipes/"]')
	if not link:
		return ""

	return _abs_url(link.get("href"))


def _find_team_link_text(context: Tag | None) -> str:
	if not context:
		return ""

	link = context.select_one('a[href*="/equipes/"]')
	if not link:
		return ""

	# Remove texto de filhos muito ruidosos, mas mantém nome visível.
	return clean_text(link.get_text(" "))


def _find_name_from_game_block(context: Tag | None, target_logo_url: str) -> str:
	"""Tenta achar nome sazonal comparando a logo no bloco de último/próximo jogo."""
	if not context or not target_logo_url:
		return ""

	target_key = image_key(target_logo_url)

	for block in context.select(".games_last_next_next"):
		imgs = block.find_all("img")
		names = []

		for strong in block.find_all("strong"):
			classes = strong.get("class") or []
			text = clean_text(strong.get_text())

			if "amarelo_clarot" in classes:
				continue

			if not text or " X " in text:
				continue

			names.append(text)

		if len(imgs) < 2 or len(names) < 2:
			continue

		for idx, img in enumerate(imgs[:2]):
			current_key = image_key(img.get("src"))
			if current_key and current_key == target_key and idx < len(names):
				return names[idx]

	return ""


def _build_aliases(
	abbreviation: str,
	season_display_name: str,
	logo_alt: str,
	link_text: str,
	team_slug: str,
) -> list[tuple[str, str]]:
	"""Monta aliases com tipo."""
	values = [
		(abbreviation, "abbreviation"),
		(season_display_name, "season_display_name"),
		(logo_alt, "logo_alt"),
		(link_text, "link_text"),
		(title_from_slug(team_slug), "slug_name"),
	]

	aliases: list[tuple[str, str]] = []
	seen = set()

	for alias, alias_type in values:
		alias = clean_text(alias)
		key = alias.lower()

		if not alias or key in seen:
			continue

		aliases.append((alias, alias_type))
		seen.add(key)

	return aliases


def _deduplicate(items: list[ParsedTeam]) -> list[ParsedTeam]:
	"""Remove duplicatas dentro da mesma temporada."""
	result = []
	seen = set()

	for item in items:
		key = (item.season_id, item.team_slug or item.abbreviation)

		if key in seen:
			continue

		result.append(item)
		seen.add(key)

	return result