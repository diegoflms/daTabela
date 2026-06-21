from __future__ import annotations

from dataclasses import dataclass
import re

from bs4 import BeautifulSoup, Tag

from src.utils.text import clean_text


class NoBoxscoreStatsError(RuntimeError):
	pass


@dataclass
class ParsedStatLine:
	side: str
	parse_model: str
	jersey_number: str
	player_name_raw: str
	is_starter: int
	minutes_text: str
	minutes_decimal: str
	points: str
	points_attempted: str
	fg_made: str
	fg_attempted: str
	fg_pct: str
	three_made: str
	three_attempted: str
	three_pct: str
	two_made: str
	two_attempted: str
	two_pct: str
	ft_made: str
	ft_attempted: str
	ft_pct: str
	offensive_rebounds: str
	defensive_rebounds: str
	total_rebounds: str
	assists: str
	steals: str
	blocks: str
	fouls_committed: str
	fouls_received: str
	turnovers: str
	dunks: str
	plus_minus: str
	efficiency: str


@dataclass
class ParsedTeamStat:
	side: str
	parse_model: str
	points: str
	points_attempted: str
	fg_made: str
	fg_attempted: str
	fg_pct: str
	three_made: str
	three_attempted: str
	three_pct: str
	two_made: str
	two_attempted: str
	two_pct: str
	ft_made: str
	ft_attempted: str
	ft_pct: str
	offensive_rebounds: str
	defensive_rebounds: str
	total_rebounds: str
	assists: str
	steals: str
	blocks: str
	fouls_committed: str
	fouls_received: str
	turnovers: str
	dunks: str
	plus_minus: str
	efficiency: str
	collective_offensive_rebounds: str
	collective_defensive_rebounds: str
	collective_total_rebounds: str


@dataclass
class ParsedBoxscore:
	player_stats: list[ParsedStatLine]
	team_stats: list[ParsedTeamStat]
	parse_model: str


def parse_boxscore_html(html: str) -> ParsedBoxscore:
	"""Extrai estatísticas individuais e totais do boxscore."""
	soup = BeautifulSoup(html, "lxml")

	tables = _find_boxscore_tables(soup)

	if len(tables) < 2:
		raise NoBoxscoreStatsError("Nenhuma dupla de tabelas de boxscore encontrada.")

	player_stats: list[ParsedStatLine] = []
	team_stats: list[ParsedTeamStat] = []

	for side, table, parse_model in tables:
		players, team = _parse_stats_table(table, side, parse_model)
		player_stats.extend(players)

		if team:
			team_stats.append(team)

	if not player_stats:
		raise NoBoxscoreStatsError(
			"Tabelas encontradas, mas sem linhas úteis de jogadores."
		)

	if len(team_stats) != 2:
		raise NoBoxscoreStatsError(
			f"Boxscore incompleto: esperado 2 linhas de time, encontrado {len(team_stats)}."
		)

	model = "mixed"
	if tables:
		models = {item[2] for item in tables}
		model = next(iter(models)) if len(models) == 1 else "mixed"

	return ParsedBoxscore(
		player_stats=player_stats,
		team_stats=team_stats,
		parse_model=model,
	)


def _find_boxscore_tables(soup: BeautifulSoup) -> list[tuple[str, Tag, str]]:
	"""Localiza tabelas gerais dos dois times em qualquer variação conhecida."""
	tables: list[tuple[str, Tag, str]] = []

	# 1) Modelo novo explícito: home/away.
	explicit_new = [
		(
			"home",
			soup.select_one(
				".stats_real_time_table_home table.real_time_table_stats[idq='0']"
			),
			"realtime",
		),
		(
			"away",
			soup.select_one(
				".stats_real_time_table_away table.real_time_table_stats[idq='0']"
			),
			"realtime",
		),
	]

	if explicit_new[0][1] and explicit_new[1][1]:
		return explicit_new

	# 2) Modelo antigo explícito: home/away.
	explicit_old = [
		(
			"home",
			soup.select_one("#team_home_stats table[idx='general']"),
			"classic",
		),
		(
			"away",
			soup.select_one("#team_away_stats table[idx='general']"),
			"classic",
		),
	]

	if explicit_old[0][1] and explicit_old[1][1]:
		return explicit_old

	# 3) Fallback forte: qualquer tabela realtime idq=0 com cara de boxscore.
	realtime_candidates = [
		table
		for table in soup.select("table.real_time_table_stats[idq='0']")
		if _looks_like_boxscore_table(table)
	]

	if len(realtime_candidates) >= 2:
		return [
			("home", realtime_candidates[0], "realtime_fallback_scan"),
			("away", realtime_candidates[1], "realtime_fallback_scan"),
		]

	# 4) Fallback antigo: qualquer tabela general com cara de boxscore.
	classic_candidates = [
		table
		for table in soup.select("table.team_general_table[idx='general'], table[idx='general']")
		if _looks_like_boxscore_table(table)
	]

	if len(classic_candidates) >= 2:
		return [
			("home", classic_candidates[0], "classic_fallback_scan"),
			("away", classic_candidates[1], "classic_fallback_scan"),
		]

	# 5) Último fallback: qualquer table com headers de boxscore.
	generic_candidates = [
		table
		for table in soup.find_all("table")
		if _looks_like_boxscore_table(table)
	]

	if len(generic_candidates) >= 2:
		return [
			("home", generic_candidates[0], "generic_fallback_scan"),
			("away", generic_candidates[1], "generic_fallback_scan"),
		]

	return []

def _looks_like_boxscore_table(table: Tag) -> bool:
	"""Confere se a tabela parece conter estatísticas reais de jogadores."""
	headers = _headers_from_table(table)
	header_key = " ".join(headers).lower()

	has_player_headers = (
		"jogador" in header_key
		and "min" in header_key
		and ("pts" in header_key or "pontos" in header_key)
	)

	if not has_player_headers:
		return False

	player_rows = 0

	for row in _table_data_rows(table):
		cells = _cells_from_row(row)

		if _row_kind(cells) != "player":
			continue

		if _row_has_stats(cells):
			player_rows += 1

	return player_rows > 0


def _row_has_stats(cells: list[str]) -> bool:
	"""Evita aceitar tabela vazia só com cabeçalho/Total em branco."""
	if len(cells) < 5:
		return False

	joined = " ".join(cells).lower()

	if "fatal error" in joined or "erro crítico" in joined:
		return False

	stats_part = " ".join(cells[2:])

	return bool(re.search(r"\d+/\d+|\d+:\d+|\d+\.\d+|\b\d+\b", stats_part))


def _headers_from_table(table: Tag) -> list[str]:
	"""Extrai cabeçalhos reais da tabela."""
	headers = []

	for th in table.select("thead th"):
		text = clean_text(th.get_text(" ", strip=True))
		if text:
			headers.append(text)

	if headers:
		return headers

	first_row = table.find("tr")
	if not first_row:
		return []

	return [
		clean_text(cell.get_text(" ", strip=True))
		for cell in first_row.find_all(["th", "td"])
	]


def _table_data_rows(table: Tag) -> list[Tag]:
	"""Pega linhas de dados, incluindo tbody e tfoot."""
	rows = table.select("tbody tr, tfoot tr")

	if rows:
		return rows

	return table.find_all("tr")


def _cells_from_row(row: Tag) -> list[str]:
	"""Extrai células normalizadas."""
	return [
		clean_text(cell.get_text(" ", strip=True))
		for cell in row.find_all(["td", "th"])
	]


def _build_team_total_from_players(
	players: list[ParsedStatLine],
	side: str,
	parse_model: str,
) -> ParsedTeamStat | None:
	"""Calcula total do time quando a linha Total/Equipe não existe."""
	if not players:
		return None

	def sum_field(field: str) -> str:
		total = 0

		for player in players:
			value = getattr(player, field, "")
			try:
				total += int(float(value or 0))
			except ValueError:
				pass

		return str(total)

	fg_made = sum_field("fg_made")
	fg_attempted = sum_field("fg_attempted")
	three_made = sum_field("three_made")
	three_attempted = sum_field("three_attempted")
	two_made = sum_field("two_made")
	two_attempted = sum_field("two_attempted")
	ft_made = sum_field("ft_made")
	ft_attempted = sum_field("ft_attempted")

	return ParsedTeamStat(
		side=side,
		parse_model=f"{parse_model}_computed_total",
		points=sum_field("points"),
		points_attempted=sum_field("points_attempted"),
		fg_made=fg_made,
		fg_attempted=fg_attempted,
		fg_pct=_percentage(fg_made, fg_attempted),
		three_made=three_made,
		three_attempted=three_attempted,
		three_pct=_percentage(three_made, three_attempted),
		two_made=two_made,
		two_attempted=two_attempted,
		two_pct=_percentage(two_made, two_attempted),
		ft_made=ft_made,
		ft_attempted=ft_attempted,
		ft_pct=_percentage(ft_made, ft_attempted),
		offensive_rebounds=sum_field("offensive_rebounds"),
		defensive_rebounds=sum_field("defensive_rebounds"),
		total_rebounds=sum_field("total_rebounds"),
		assists=sum_field("assists"),
		steals=sum_field("steals"),
		blocks=sum_field("blocks"),
		fouls_committed=sum_field("fouls_committed"),
		fouls_received=sum_field("fouls_received"),
		turnovers=sum_field("turnovers"),
		dunks=sum_field("dunks"),
		plus_minus=sum_field("plus_minus"),
		efficiency=sum_field("efficiency"),
		collective_offensive_rebounds="",
		collective_defensive_rebounds="",
		collective_total_rebounds="",
	)

def _parse_stats_table(
	table: Tag,
	side: str,
	parse_model: str,
) -> tuple[list[ParsedStatLine], ParsedTeamStat | None]:
	headers = _headers_from_table(table)
	has_jo = any(header.upper() == "JO" for header in headers)

	players: list[ParsedStatLine] = []
	team_total: ParsedTeamStat | None = None
	collective = {
		"offensive_rebounds": "",
		"defensive_rebounds": "",
		"total_rebounds": "",
	}

	for row in _table_data_rows(table):
		cells = _cells_from_row(row)

		if not cells or cells == headers:
			continue

		row_kind = _row_kind(cells)

		if row_kind == "collective":
			collective = _parse_collective_row(cells, has_jo)
			continue

		if row_kind == "team_total":
			team_total = _parse_team_total_row(cells, side, parse_model, has_jo)
			continue

		if row_kind == "player":
			parsed = _parse_player_row(cells, side, parse_model, has_jo)
			if parsed:
				players.append(parsed)

	if team_total:
		team_total.collective_offensive_rebounds = collective["offensive_rebounds"]
		team_total.collective_defensive_rebounds = collective["defensive_rebounds"]
		team_total.collective_total_rebounds = collective["total_rebounds"]
	else:
		team_total = _build_team_total_from_players(
			players=players,
			side=side,
			parse_model=parse_model,
		)

	return players, team_total

	return players, team_total


def _row_kind(cells: list[str]) -> str:
	joined = " ".join(cells).lower()

	if "ações coletivas" in joined or "acoes coletivas" in joined:
		return "collective"

	first_two = [cell.lower().strip() for cell in cells[:2]]

	if any(cell in {"total", "equipe"} for cell in first_two):
		return "team_total"

	first_cell = clean_text(cells[0]).replace(" ", "") if cells else ""

	if first_cell.startswith("#") and len(cells) > 1 and clean_text(cells[1]):
		return "player"

	if first_cell.isdigit() and len(cells) > 1 and clean_text(cells[1]):
		second = clean_text(cells[1]).lower()

		if second not in {
			"jogador",
			"total",
			"equipe",
			"ações coletivas",
			"acoes coletivas",
		}:
			return "player"

	return "unknown"


def _parse_player_row(
	cells: list[str],
	side: str,
	parse_model: str,
	has_jo: bool,
) -> ParsedStatLine | None:
	try:
		jersey = _parse_jersey(cells[0])
		name_raw, is_starter = _clean_player_name(cells[1])

		if not name_raw:
			return None

		if has_jo:
			minutes = cells[3]
			pts = cells[4]
			reb = cells[5]
			assists = cells[6]
			three = cells[7]
			two = cells[8]
			ft = cells[9]
			steals = cells[10]
			blocks = cells[11]
			fouls_committed = cells[12]
			fouls_received = cells[13]
			turnovers = cells[14]
			dunks = cells[15]
			plus_minus = cells[16]
			efficiency = cells[17]
		else:
			minutes = cells[2]
			pts = cells[3]
			three = cells[4]
			two = cells[5]
			ft = cells[6]
			reb = cells[7]
			assists = cells[8]
			steals = cells[9]
			blocks = cells[10]
			fouls_committed = cells[11]
			fouls_received = cells[12]
			turnovers = cells[13]
			dunks = cells[14]
			plus_minus = cells[15]
			efficiency = cells[16]

		line = _build_stat_line(
			side=side,
			parse_model=parse_model,
			jersey_number=jersey,
			player_name_raw=name_raw,
			is_starter=is_starter,
			minutes=minutes,
			pts=pts,
			three=three,
			two=two,
			ft=ft,
			reb=reb,
			assists=assists,
			steals=steals,
			blocks=blocks,
			fouls_committed=fouls_committed,
			fouls_received=fouls_received,
			turnovers=turnovers,
			dunks=dunks,
			plus_minus=plus_minus,
			efficiency=efficiency,
		)

		if _is_dnp_stat_line(line):
			return None

		return line

	except IndexError:
		return None


def _parse_team_total_row(
	cells: list[str],
	side: str,
	parse_model: str,
	has_jo: bool,
) -> ParsedTeamStat | None:
	try:
		if has_jo:
			# Modelo antigo: Equipe, JO, Min, Pts, Reb, AS, 3P, 2P, LL...
			pts = cells[3]
			reb = cells[4]
			assists = cells[5]
			three = cells[6]
			two = cells[7]
			ft = cells[8]
			steals = cells[9]
			blocks = cells[10]
			fouls_committed = cells[11]
			fouls_received = cells[12]
			turnovers = cells[13]
			dunks = cells[14]
			plus_minus = cells[15]
			efficiency = cells[16]
		else:
			# Modelo novo: "", Total, Min, Pts, 3P, 2P, LL, Reb...
			pts = cells[3]
			three = cells[4]
			two = cells[5]
			ft = cells[6]
			reb = cells[7]
			assists = cells[8]
			steals = cells[9]
			blocks = cells[10]
			fouls_committed = cells[11]
			fouls_received = cells[12]
			turnovers = cells[13]
			dunks = cells[14]
			plus_minus = cells[15]
			efficiency = cells[16]

		line = _build_stat_line(
			side=side,
			parse_model=parse_model,
			jersey_number="",
			player_name_raw="Total",
			is_starter=0,
			minutes="",
			pts=pts,
			three=three,
			two=two,
			ft=ft,
			reb=reb,
			assists=assists,
			steals=steals,
			blocks=blocks,
			fouls_committed=fouls_committed,
			fouls_received=fouls_received,
			turnovers=turnovers,
			dunks=dunks,
			plus_minus=plus_minus,
			efficiency=efficiency,
		)

		return ParsedTeamStat(
			side=side,
			parse_model=parse_model,
			points=line.points,
			points_attempted=line.points_attempted,
			fg_made=line.fg_made,
			fg_attempted=line.fg_attempted,
			fg_pct=line.fg_pct,
			three_made=line.three_made,
			three_attempted=line.three_attempted,
			three_pct=line.three_pct,
			two_made=line.two_made,
			two_attempted=line.two_attempted,
			two_pct=line.two_pct,
			ft_made=line.ft_made,
			ft_attempted=line.ft_attempted,
			ft_pct=line.ft_pct,
			offensive_rebounds=line.offensive_rebounds,
			defensive_rebounds=line.defensive_rebounds,
			total_rebounds=line.total_rebounds,
			assists=line.assists,
			steals=line.steals,
			blocks=line.blocks,
			fouls_committed=line.fouls_committed,
			fouls_received=line.fouls_received,
			turnovers=line.turnovers,
			dunks=line.dunks,
			plus_minus=line.plus_minus,
			efficiency=line.efficiency,
			collective_offensive_rebounds="",
			collective_defensive_rebounds="",
			collective_total_rebounds="",
		)

	except IndexError:
		return None


def _parse_collective_row(cells: list[str], has_jo: bool) -> dict[str, str]:
	reb_index = 4 if has_jo else 7

	try:
		off, deff, total = _parse_rebounds(cells[reb_index])
	except IndexError:
		off, deff, total = "", "", ""

	return {
		"offensive_rebounds": off,
		"defensive_rebounds": deff,
		"total_rebounds": total,
	}


def _build_stat_line(
	side: str,
	parse_model: str,
	jersey_number: str,
	player_name_raw: str,
	is_starter: int,
	minutes: str,
	pts: str,
	three: str,
	two: str,
	ft: str,
	reb: str,
	assists: str,
	steals: str,
	blocks: str,
	fouls_committed: str,
	fouls_received: str,
	turnovers: str,
	dunks: str,
	plus_minus: str,
	efficiency: str,
) -> ParsedStatLine:
	points, points_attempted, points_pct = _parse_ct_pct(pts)
	three_made, three_attempted, three_pct = _parse_ct_pct(three)
	two_made, two_attempted, two_pct = _parse_ct_pct(two)
	ft_made, ft_attempted, ft_pct = _parse_ct_pct(ft)
	off_reb, def_reb, total_reb = _parse_rebounds(reb)

	fg_made = _sum_ints(two_made, three_made)
	fg_attempted = _sum_ints(two_attempted, three_attempted)
	fg_pct = _percentage(fg_made, fg_attempted)

	return ParsedStatLine(
		side=side,
		parse_model=parse_model,
		jersey_number=jersey_number,
		player_name_raw=player_name_raw,
		is_starter=is_starter,
		minutes_text=minutes,
		minutes_decimal=_minutes_to_decimal(minutes),
		points=points,
		points_attempted=points_attempted,
		fg_made=fg_made,
		fg_attempted=fg_attempted,
		fg_pct=fg_pct or points_pct,
		three_made=three_made,
		three_attempted=three_attempted,
		three_pct=three_pct,
		two_made=two_made,
		two_attempted=two_attempted,
		two_pct=two_pct,
		ft_made=ft_made,
		ft_attempted=ft_attempted,
		ft_pct=ft_pct,
		offensive_rebounds=off_reb,
		defensive_rebounds=def_reb,
		total_rebounds=total_reb,
		assists=_number(assists),
		steals=_number(steals),
		blocks=_number(blocks),
		fouls_committed=_number(fouls_committed),
		fouls_received=_number(fouls_received),
		turnovers=_number(turnovers),
		dunks=_number(dunks),
		plus_minus=_number(plus_minus),
		efficiency=_number(efficiency),
	)

def _is_dnp_stat_line(line: ParsedStatLine) -> bool:
	"""Descarta jogador listado no boxscore mas que não entrou em quadra."""
	try:
		minutes = float(line.minutes_decimal or 0)
	except ValueError:
		minutes = 0

	stat_fields = [
		"points",
		"fg_made",
		"fg_attempted",
		"three_made",
		"three_attempted",
		"two_made",
		"two_attempted",
		"ft_made",
		"ft_attempted",
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
	]

	has_any_stat = False

	for field in stat_fields:
		value = getattr(line, field, "")

		try:
			if float(value or 0) != 0:
				has_any_stat = True
				break
		except ValueError:
			pass

	return minutes <= 0 and not has_any_stat

def _parse_ct_pct(value: str) -> tuple[str, str, str]:
	value = clean_text(value).replace(",", ".")

	match = re.search(r"(-?\d+(?:\.\d+)?)\s*/\s*(-?\d+(?:\.\d+)?)\s*\((-?\d+(?:\.\d+)?)\)", value)
	if match:
		return _number(match.group(1)), _number(match.group(2)), _number(match.group(3))

	match = re.search(r"(-?\d+(?:\.\d+)?)", value)
	if match:
		return _number(match.group(1)), "", ""

	return "", "", ""


def _parse_rebounds(value: str) -> tuple[str, str, str]:
	value = clean_text(value)

	match = re.search(r"(-?\d+)\s*\+\s*(-?\d+)\s+(-?\d+)", value)
	if match:
		return match.group(1), match.group(2), match.group(3)

	match = re.search(r"(-?\d+)", value)
	if match:
		return "", "", match.group(1)

	return "", "", ""


def _parse_jersey(value: str) -> str:
	value = clean_text(value)
	match = re.search(r"#\s*(\d+)", value)
	return match.group(1) if match else ""


def _clean_player_name(value: str) -> tuple[str, int]:
	value = clean_text(value)
	is_starter = 1 if "(T)" in value else 0
	value = value.replace("(T)", "")
	return clean_text(value), is_starter


def _minutes_to_decimal(value: str) -> str:
	value = clean_text(value).replace(",", ".")

	if not value:
		return ""

	if ":" in value:
		try:
			minutes, seconds = value.split(":", 1)
			total = int(minutes) + int(seconds) / 60
			return f"{total:.2f}"
		except ValueError:
			return ""

	try:
		return str(float(value)).rstrip("0").rstrip(".")
	except ValueError:
		return ""


def _sum_ints(a: str, b: str) -> str:
	try:
		return str(int(float(a or 0)) + int(float(b or 0)))
	except ValueError:
		return ""


def _percentage(made: str, attempted: str) -> str:
	try:
		made_i = int(float(made))
		attempted_i = int(float(attempted))
	except ValueError:
		return ""

	if attempted_i == 0:
		return "0"

	return f"{100 * made_i / attempted_i:.1f}".rstrip("0").rstrip(".")


def _number(value: str) -> str:
	value = clean_text(value).replace(",", ".")
	match = re.search(r"-?\d+(?:\.\d+)?", value)
	if not match:
		return ""

	number = match.group(0)

	if number.endswith(".00"):
		return number[:-3]

	return number


def _ancestor_classes(tag: Tag) -> set[str]:
	classes = set()
	parent = tag.parent

	while parent:
		for cls in parent.get("class") or []:
			classes.add(cls)
		parent = parent.parent

	return classes


def _ancestor_ids(tag: Tag) -> set[str]:
	ids = set()
	parent = tag.parent

	while parent:
		if parent.get("id"):
			ids.add(parent.get("id"))
		parent = parent.parent

	return ids