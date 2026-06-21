from src.scraping.parsers.standings_parser import parse_teams_from_standings
from src.scraping.teams_scraper import season_name_to_url_path


def test_season_name_to_url_path():
	assert season_name_to_url_path("2009-10") == "2009-2010"
	assert season_name_to_url_path("2024-25") == "2024-2025"


def test_parse_team_from_standings_like_html():
	html = """
	<table>
	  <tr>
		<td><div class="logo"><img src="https://lnb.com.br/logo-flamengo-150x150.png" alt="Flamengo"></div></td>
		<td><strong class="team_first">FLA</strong></td>
	  </tr>
	  <tr>
		<td colspan="5">
		  <a href="https://lnb.com.br/equipes/flamengo/">Flamengo</a>
		  <div class="games_last_next_next">
			<img src="https://lnb.com.br/logo-flamengo-150x150.png" alt="">
			<strong>Flamengo</strong>
			X
			<strong>Minas</strong>
			<img src="https://lnb.com.br/logo-minas-150x150.png" alt="">
			<br>
			<strong class="amarelo_clarot">89 X 80</strong>
		  </div>
		</td>
	  </tr>
	</table>
	"""

	teams = parse_teams_from_standings(html, season_id=1)

	assert len(teams) == 1
	assert teams[0].abbreviation == "FLA"
	assert teams[0].season_display_name == "Flamengo"
	assert teams[0].team_slug == "flamengo"
	assert ("FLA", "abbreviation") in teams[0].aliases