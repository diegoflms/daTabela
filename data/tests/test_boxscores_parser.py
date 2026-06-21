from src.scraping.parsers.boxscores_parser import parse_boxscore_html


def test_parse_realtime_boxscore():
	html = """
	<div class="stats_real_time_table_home table-wrapper">
	  <table class="real_time_table_stats" idq="0">
		<thead>
		  <tr>
			<th>Nr.</th><th>Jogador</th><th>Min</th><th>Pts C/T %</th>
			<th>3 P C/T %</th><th>2 P C/T %</th><th>LL C/T %</th>
			<th>RO+RD RT</th><th>AS</th><th>BR</th><th>TO</th>
			<th>FC</th><th>FR</th><th>ER</th><th>EN</th><th>+-</th><th>EF</th>
		  </tr>
		</thead>
		<tbody>
		  <tr>
			<td># 3</td><td>Bennett (T)</td><td>36:54</td><td>12/26 (46.2)</td>
			<td>1/4 (25.0)</td><td>3/5 (60.0)</td><td>3/4 (75.0)</td>
			<td>0+0 0</td><td>3</td><td>0</td><td>0</td><td>2</td><td>4</td>
			<td>1</td><td>0</td><td>4</td><td>8</td>
		  </tr>
		  <tr>
			<td></td><td>Ações coletivas</td><td></td><td></td><td></td><td></td><td></td>
			<td>0+4 4</td><td></td><td></td><td></td><td>0</td><td></td><td>0</td><td></td><td></td><td></td>
		  </tr>
		  <tr>
			<td></td><td>Total</td><td></td><td>75/189 (39.7)</td>
			<td>8/31 (25.8)</td><td>17/38 (44.7)</td><td>17/20 (85.0)</td>
			<td>7+30 37</td><td>15</td><td>6</td><td>2</td><td>21</td><td>19</td>
			<td>11</td><td>2</td><td>-4</td><td>77</td>
		  </tr>
		</tbody>
	  </table>
	</div>

	<div class="stats_real_time_table_away table-wrapper">
	  <table class="real_time_table_stats" idq="0">
		<thead>
		  <tr>
			<th>Nr.</th><th>Jogador</th><th>Min</th><th>Pts C/T %</th>
			<th>3 P C/T %</th><th>2 P C/T %</th><th>LL C/T %</th>
			<th>RO+RD RT</th><th>AS</th><th>BR</th><th>TO</th>
			<th>FC</th><th>FR</th><th>ER</th><th>EN</th><th>+-</th><th>EF</th>
		  </tr>
		</thead>
		<tbody>
		  <tr>
			<td>#7</td><td>Renato (T)</td><td>36:59</td><td>19/33 (57.6)</td>
			<td>3/6 (50.0)</td><td>4/6 (66.7)</td><td>2/3 (66.7)</td>
			<td>2+3 5</td><td>1</td><td>1</td><td>0</td><td>4</td><td>3</td>
			<td>1</td><td>0</td><td>6</td><td>19</td>
		  </tr>
		  <tr>
			<td></td><td>Total</td><td></td><td>79/178 (44.4)</td>
			<td>8/22 (36.4)</td><td>19/44 (43.2)</td><td>17/24 (70.8)</td>
			<td>9+33 42</td><td>18</td><td>6</td><td>0</td><td>19</td><td>20</td>
			<td>12</td><td>2</td><td>4</td><td>87</td>
		  </tr>
		</tbody>
	  </table>
	</div>
	"""

	parsed = parse_boxscore_html(html)

	assert len(parsed.player_stats) == 2
	assert len(parsed.team_stats) == 2

	player = parsed.player_stats[0]
	assert player.player_name_raw == "Bennett"
	assert player.jersey_number == "3"
	assert player.is_starter == 1
	assert player.minutes_decimal == "36.90" # tava 36.9
	assert player.points == "12"
	assert player.three_made == "1"
	assert player.two_made == "3"
	assert player.ft_made == "3"

	team = parsed.team_stats[0]
	assert team.points == "75"
	assert team.total_rebounds == "37"
	assert team.collective_total_rebounds == "4"