from dataclasses import dataclass
import re
from urllib.parse import urljoin, unquote

from bs4 import BeautifulSoup, Tag

from src.utils.text import clean_text, extract_player_slug_from_url, slugify


BASE_URL = "https://lnb.com.br"


@dataclass
class ParsedPlayerLink:
	season_id: int
	player_url: str
	player_slug: str
	display_name: str
	jersey_number: str
	team_name_raw: str
	team_url: str
	source_url: str


@dataclass
class ParsedPlayerProfile:
	player_url: str
	player_slug: str
	full_name: str
	display_name: str
	profile_jersey_number: str
	photo_url: str
	birth_date: str
	position: str
	naturality: str
	height_cm: str
	weight_kg: str


def parse_player_links_from_stats(
	html: str,
	season_id: int,
	source_url: str,
) -> list[ParsedPlayerLink]:
	"""Extrai URLs de atletas da tabela de estatísticas."""
	soup = BeautifulSoup(html, "lxml")
	rows = soup.select("table.stats-table-catch tbody tr")

	players: list[ParsedPlayerLink] = []

	for row in rows:
		item = _parse_stats_row(row, season_id, source_url)
		if item:
			players.append(item)

	return _deduplicate_links(players)


def parse_player_profile(html: str, player_url: str) -> ParsedPlayerProfile:
	"""Extrai dados cadastrais da página individual do atleta."""
	soup = BeautifulSoup(html, "lxml")

	profile_table = (
		soup.select_one("table.ficha_tecnica_athlete_stats.hide-for-small-only")
		or soup.select_one("table.ficha_tecnica_athlete_stats")
	)

	data = _parse_profile_table(profile_table)

	header_name, header_number = _parse_header_name_and_number(soup)

	photo_img = soup.select_one(".photo_athlete_blue img")
	photo_url = _abs_url(photo_img.get("src")) if photo_img else ""

	full_name = data.get("Nome") or header_name or _name_from_slug(player_url)
	display_name = header_name or _short_display_name(full_name)

	height_cm, weight_kg = _parse_height_weight(data.get("Altura / Peso", ""))

	return ParsedPlayerProfile(
		player_url=player_url,
		player_slug=extract_player_slug_from_url(player_url),
		full_name=full_name,
		display_name=display_name,
		profile_jersey_number=header_number,
		photo_url=photo_url,
		birth_date=_to_iso_date(data.get("Data de Nascimento", "")),
		position=data.get("Posição", ""),
		naturality=data.get("Naturalidade", ""),
		height_cm=height_cm,
		weight_kg=weight_kg,
	)


def _parse_stats_row(
	row: Tag,
	season_id: int,
	source_url: str,
) -> ParsedPlayerLink | None:
	cells = row.find_all("td")
	if len(cells) < 3:
		return None

	player_link = cells[1].select_one('a[href*="/atletas/"]')
	if not player_link:
		return None

	player_url = _abs_url(player_link.get("href"))
	player_slug = extract_player_slug_from_url(player_url)

	display_name, jersey_number = _parse_link_name_and_number(
		player_link.get_text(" ", strip=True)
	)

	team_link = cells[2].select_one('a[href*="/equipes/"]')
	team_name_raw = clean_text(cells[2].get_text(" ", strip=True))
	team_url = _abs_url(team_link.get("href")) if team_link else ""

	if not player_url or not player_slug:
		return None

	return ParsedPlayerLink(
		season_id=season_id,
		player_url=player_url,
		player_slug=player_slug,
		display_name=display_name,
		jersey_number=jersey_number,
		team_name_raw=team_name_raw,
		team_url=team_url,
		source_url=source_url,
	)


def _parse_link_name_and_number(value: str) -> tuple[str, str]:
	value = clean_text(value)

	match = re.search(r"#\s*(\d+)\s*$", value)
	if not match:
		return value, ""

	number = match.group(1)
	name = clean_text(value[: match.start()])

	return name, number


def _parse_profile_table(table: Tag | None) -> dict[str, str]:
	"""Lê pares label/valor da ficha técnica."""
	if not table:
		return {}

	data: dict[str, str] = {}

	for row in table.select("tr"):
		cells = [clean_text(td.get_text(" ", strip=True)) for td in row.select("td")]

		# A tabela desktop vem como: label, valor, label, valor.
		for idx in range(0, len(cells) - 1, 2):
			label = cells[idx]
			value = cells[idx + 1]

			if not label:
				continue

			# Descartamos campos não confiáveis para este scraper.
			if label in {"Equipe", "Equipe(s)", "Participação no Jogo das Estrelas"}:
				continue

			data[label] = value

	return data


def _parse_header_name_and_number(soup: BeautifulSoup) -> tuple[str, str]:
	"""Extrai '#10 Alex' do cabeçalho, quando existir."""
	for h1 in soup.find_all("h1"):
		text = clean_text(h1.get_text(" ", strip=True))

		match = re.match(r"^#\s*(\d+)\s+(.+)$", text)
		if match:
			return clean_text(match.group(2)), match.group(1)

	return "", ""


def _parse_height_weight(value: str) -> tuple[str, str]:
	value = clean_text(value).replace(",", ".")

	height_cm = ""
	weight_kg = ""

	height_match = re.search(r"(\d+(?:\.\d+)?)", value)
	if height_match:
		height = float(height_match.group(1))

		if height < 3:
			height_cm = str(int(round(height * 100)))
		else:
			height_cm = str(int(round(height)))

	weight_match = re.search(r"/?\s*(\d+(?:\.\d+)?)\s*kg", value, flags=re.I)
	if weight_match:
		weight_kg = str(float(weight_match.group(1))).rstrip("0").rstrip(".")

	return height_cm, weight_kg


def _to_iso_date(value: str) -> str:
	value = clean_text(value)

	if not value:
		return ""

	try:
		day, month, year = value.split("/")
		return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
	except ValueError:
		return value


def _short_display_name(full_name: str) -> str:
	pieces = clean_text(full_name).split()
	return pieces[0] if pieces else ""


def _name_from_slug(url: str) -> str:
	slug = extract_player_slug_from_url(url)
	return clean_text(unquote(slug).replace("-", " ").title())


def _abs_url(url: str | None) -> str:
	if not url:
		return ""
	return urljoin(BASE_URL, url)


def _deduplicate_links(items: list[ParsedPlayerLink]) -> list[ParsedPlayerLink]:
	result = []
	seen = set()

	for item in items:
		key = (item.season_id, item.player_slug)

		if key in seen:
			continue

		seen.add(key)
		result.append(item)

	return result