from src.scraping.parsers.games_parser import parse_games_from_html


def test_parse_games_from_html():
	html = """
	<table class="table_matches_table">
	  <tbody>
		<tr class="with-hotel">
		  <td class="position_value show-for-medium" data-label="JOGO" data-real-id="1647">1</td>

		  <td class="date_value show-for-medium" data-label="DATA">
			<span>28/01/2009</span>
			<span>18:30</span>
		  </td>

		  <td class="home_team_value show-for-medium" data-label="CASA">
			<span class="team-shortname">Espírito Santo</span>
		  </td>

		  <td class="logo_home_team show-for-medium">
			<img src="https://lnb.com.br/wp-content/uploads/2013/10/Espirito-Santo-Basquketball.png">
		  </td>

		  <td class="score_value show-for-medium">
			<a href="https://lnb.com.br/noticias/espirito-santo-x-araraquara-28012009/"
			   class="match_score_relatorio">
			  <span class="home">77</span>
			  X
			  <span class="away">56</span>
			  <span class="report">VER RELATÓRIO</span>
			</a>
		  </td>

		  <td class="logo_visitor_team show-for-medium">
			<img src="https://lnb.com.br/wp-content/uploads/2012/02/Araraquara.png">
		  </td>

		  <td class="visitor_team_value show-for-medium" data-label="VISITANTE">
			<span class="team-shortname">Araraquara</span>
		  </td>

		  <td class="hide-for-medium matche_for_small">
			<strong>ESB <img src="x.png"></strong>
			<a class="match_score_relatorio">
			  <span class="home">77</span>
			  X
			  <span class="away">56</span>
			</a>
			<strong><img src="y.png"> ARA</strong>
		  </td>

		  <td class="game_value hide_value" data-label="RODADA">
			<span class="number">1ª</span>
			<span class="the-label">RODADA</span>
		  </td>

		  <td class="stage_value hide_value" data-label="FASE">1º TURNO</td>
		  <td class="champ_value hide_value" data-label="CAMPEONATO">2008/2009</td>
		  <td class="gym_value hide_value" data-label="GINÁSIO"></td>
		</tr>
	  </tbody>
	</table>
	"""

	games = parse_games_from_html(
		html=html,
		season_id=1,
		source_url="https://lnb.com.br/nbb/tabela-de-jogos/?season%5B%5D=1",
	)

	assert len(games) == 1

	game = games[0]

	assert game.season_id == 1
	assert game.lnb_game_id == "1647"
	assert game.game_number == "1"
	assert game.game_date == "28/01/2009"
	assert game.game_time == "18:30"
	assert game.home_team_name == "Espírito Santo"
	assert game.away_team_name == "Araraquara"
	assert game.home_team_abbr == "ESB"
	assert game.away_team_abbr == "ARA"
	assert game.home_score == "77"
	assert game.away_score == "56"
	assert game.round == "1ª RODADA"
	assert game.phase == "1º TURNO"
	assert game.status == "finished"
	assert game.boxscore_url.endswith("/espirito-santo-x-araraquara-28012009/")