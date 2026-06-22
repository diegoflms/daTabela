const labelMap: Record<string, string> = {
  // Entidades básicas
  player_name: 'Jogador',
  entity_player_name: 'Jogador',
  player_slug: 'Slug Jogador',
  player_id: 'ID Jogador',
  
  team_name: 'Time',
  entity_team_name: 'Time',
  team_slug: 'Slug Time',
  team_id: 'ID Time',
  team_abbreviation: 'Sigla',
  abbreviation: 'Sigla',
  home_team_name: 'Mandante',
  away_team_name: 'Visitante',
  score: 'Placar',
  ap_pct: 'AP(%)',
  result: 'Res',
  
  opponent_team_name: 'Adversário',
  entity_opponent_team_name: 'Adversário',
  opponent_team_id: 'ID Adversário',
  
  // Datas e info do jogo
  game_date: 'Data',
  date: 'Data',
  game_id: 'ID Jogo',
  season_id: 'Temporada',
  season_name: 'Temporada',
  seasons_count: 'Temporadas',
  phase: 'Fase',
  stage: 'Etapa',
  round: 'Rodada',
  arena: 'Arena',
  venue: 'Local',
  city: 'Cidade',
  state: 'UF',
  
  // Estatísticas de jogos e gerais
  points: 'PTS',
  pts: 'PTS',
  points_total: 'PTS Total',
  ranking_value: 'Valor',
  
  rebounds: 'REB',
  reb: 'REB',
  total_rebounds: 'REB',
  rebounds_total: 'REB Total',
  offensive_rebounds: 'REBO',
  offensive_rebounds_total: 'REBO Total',
  offensive_rebounds_per_game: 'REBO',
  defensive_rebounds: 'REBD',
  defensive_rebounds_total: 'REBD Total',
  defensive_rebounds_per_game: 'REBD',
  
  assists: 'AST',
  ast: 'AST',
  assists_total: 'AST Total',
  
  steals: 'STL',
  stl: 'STL',
  steals_total: 'STL Total',
  
  blocks: 'BLK',
  blk: 'BLK',
  blocks_total: 'BLK Total',
  
  efficiency: 'EFIC',
  eff: 'EFIC',
  efficiency_total: 'EFIC Total',
  
  minutes: 'MIN',
  min: 'MIN',
  minutes_played: 'MIN',
  minutes_total: 'MIN Total',
  minutes_per_game: 'MIN',
  points_per_game: 'PTS',
  rebounds_per_game: 'REB',
  assists_per_game: 'AST',
  steals_per_game: 'STL',
  blocks_per_game: 'BLK',
  turnovers_per_game: 'TOV',
  efficiency_per_game: 'EFIC',
  plus_minus_per_game: '+/-',
  team_names: 'Time',
  fg_pct: 'FG%',
  three_pct: '3PT%',
  two_pct: '2PT%',
  ft_pct: 'FT%',
  
  turnovers: 'TOV',
  tov: 'TOV',
  turnovers_total: 'TOV Total',
  
  fouls_committed: 'FC',
  fouls_committed_total: 'FC Total',
  fouls_committed_per_game: 'FC',
  
  fouls_received: 'FR',
  fouls_received_total: 'FR Total',
  fouls_received_per_game: 'FR',
  
  plus_minus: '+/-',
  net_rating: 'Net Rating',
  
  // Arremessos
  field_goals_made: 'FGM',
  field_goals_attempted: 'FGA',
  field_goals_pct: 'FG%',
  
  three_points_made: '3PM',
  three_points_attempted: '3PA',
  three_points_pct: '3P%',
  '3p%': '3P%',
  '3p': '3PM',
  '3pa': '3PA',
  
  two_points_made: '2PM',
  two_points_attempted: '2PA',
  two_points_pct: '2P%',
  '2p%': '2P%',
  '2p': '2PM',
  '2pa': '2PA',
  
  free_throws_made: 'FTM',
  free_throws_attempted: 'FTA',
  free_throws_pct: 'FT%',
  'll%': 'LL%', // Lances livres % (Português)
  'll': 'LLM',
  'lla': 'LLA',
  
  // Recordes, Classificação
  rank: 'Posição',
  position: 'Posição',
  wins: 'V',
  w: 'V',
  losses: 'D',
  l: 'D',
  games: 'J',
  games_played: 'J',
  gp: 'J',
  pct: 'AP(%)',
  win_pct: 'AP(%)',
  points_for: 'GP', // Gols/Pontos pró
  points_against: 'GC', // Gols/Pontos contra
  points_difference: 'SAL', // Saldo de pontos
  sal: 'SAL',
  is_champion: 'Campeão',
  dunks: 'ENT',
  dunks_total: 'ENT Total',
  games_started: 'JT',
  is_starter: 'TIT',
  competition: 'COMP',
  jersey_number: 'Nº',
  
  // Abreviaturas em maiúsculo exatas
  JO: 'JO',
  VIT: 'VIT',
  DER: 'DER',
  'AP(%)': 'AP(%)',
  PTS: 'PTS',
  FGA: 'FGA',
  FGM: 'FGM',
  'FG%': 'FG%',
  '3PA': '3PA',
  '3PM': '3PM',
  '3PT%': '3PT%',
  '2PA': '2PA',
  '2PM': '2PM',
  '2PT%': '2PT%',
  FTA: 'FTA',
  FTM: 'FTM',
  'FT%': 'FT%',
  REB: 'REB',
  OREB: 'OREB',
  DREB: 'DREB',
  AST: 'AST',
  STL: 'STL',
  BLK: 'BLK',
  TOV: 'TOV',
  FC: 'FC',
  FR: 'FR',
  EF: 'EF',
  '+/-': '+/-',
  MIN: 'MIN',

  // Custom mappings for /ask raw columns
  player_name_raw: 'Jogador',
  minutes_decimal: 'MIN',
  points_attempted: 'PTS Tent.',
  fg_made: 'FGM',
  fg_attempted: 'FGA',
  three_made: '3PM',
  three_attempted: '3PA',
  two_made: '2PM',
  two_attempted: '2PA',
  ft_made: 'FTM',
  ft_attempted: 'FTA',
  game_game_date: 'Data',
  game_home_score: 'Placar (M)',
  game_away_score: 'Placar (V)',
  game_phase: 'Fase',
};

export const formatColumnLabel = (column: string): string => {
  if (!column) return '';
  
  const normalized = column.trim().toLowerCase();
  
  // 1. Procurar no mapa
  if (labelMap[normalized] !== undefined) {
    return labelMap[normalized];
  }
  
  if (labelMap[column] !== undefined) {
    return labelMap[column];
  }
  
  // 2. Fallback amigável
  // Substitui _ por espaço e capitaliza
  return column
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
};
