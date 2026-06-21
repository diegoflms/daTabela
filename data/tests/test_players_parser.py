from src.scraping.parsers.players_parser import (
	parse_player_links_from_stats,
	parse_player_profile,
)


def test_parse_player_links_from_stats():
	html = """
	<table class="tablesorter stats-table-catch">
	  <tbody>
		<tr>
		  <td>1</td>
		  <td>
			<a href="https://lnb.com.br/atletas/marcelo-magalh%c3%a3es-machado/">
			  Marcelinho #4
			</a>
		  </td>
		  <td>
			<a href="https://lnb.com.br/equipes/flamengo/">Flamengo</a>
		  </td>
		  <td data-sort-value="39">39</td>
		</tr>
	  </tbody>
	</table>
	"""

	links = parse_player_links_from_stats(
		html=html,
		season_id=1,
		source_url="https://lnb.com.br/nbb/estatisticas/eficiencia/?season%5B%5D=1",
	)

	assert len(links) == 1
	assert links[0].display_name == "Marcelinho"
	assert links[0].jersey_number == "4"
	assert links[0].player_slug == "marcelo-magalhaes-machado"
	assert links[0].team_name_raw == "Flamengo"


def test_parse_player_profile():
	html = """
	<html>
	  <body>
		<h1>#10 Alex</h1>

		<table class="ficha_tecnica_athlete_stats hide-for-small-only">
		  <tbody>
			<tr>
			  <td>Nome</td>
			  <td>Alex Ribeiro Garcia</td>
			  <td>Posição</td>
			  <td>Ala</td>
			</tr>
			<tr>
			  <td>Equipe(s)</td>
			  <td>Bauru</td>
			  <td>Naturalidade</td>
			  <td>Orlândia (SP)</td>
			</tr>
			<tr>
			  <td>Data de Nascimento</td>
			  <td>04/03/1980</td>
			  <td>Altura / Peso</td>
			  <td>1.91 / 100kg</td>
			</tr>
			<tr>
			  <td>Participação no Jogo das Estrelas</td>
			  <td>16</td>
			  <td></td>
			  <td></td>
			</tr>
		  </tbody>
		</table>

		<div class="photo_athlete_blue">
		  <img src="https://lnb.com.br/wp-content/uploads/2016/10/10-ALEX-2.png">
		</div>
	  </body>
	</html>
	"""

	player = parse_player_profile(
		html=html,
		player_url="https://lnb.com.br/atletas/alex-ribeiro-garcia/",
	)

	assert player.full_name == "Alex Ribeiro Garcia"
	assert player.display_name == "Alex"
	assert player.profile_jersey_number == "10"
	assert player.position == "Ala"
	assert player.naturality == "Orlândia (SP)"
	assert player.birth_date == "1980-03-04"
	assert player.height_cm == "191"
	assert player.weight_kg == "100"
	assert player.photo_url.endswith("10-ALEX-2.png")