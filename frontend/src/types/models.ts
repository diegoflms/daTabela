export interface Season {
  id: number;
  name: string;
  slug: string;
  start_year: number;
  end_year: number;
  is_current: number; // SQLite uses 0 or 1
}

export interface Team {
  id: number;
  name: string;
  full_name: string;
  slug: string;
  city?: string;
  state?: string;
  abbreviation?: string;
  short_name?: string;
  arena_name?: string;
  coach?: string;
  titles_nbb?: number;
  titles_super_8?: number;
  canonical_name?: string;
  logo_url?: string | null;
  first_seen_season_id?: number;
  last_seen_season_id?: number;
  is_active?: number;
}

export interface Player {
  id: number;
  name: string;
  full_name: string;
  slug: string;
  nickname?: string;
  birthplace?: string;
  position?: string;
  height?: string;
  weight?: string;
  birth_date?: string;
  years_in_league?: number;
  current_team_id?: number;
  current_team_name?: string;
  current_team_logo_url?: string | null;
  age?: number;
  all_star_games?: number;
  jersey_number?: number;
  display_name?: string;
  photo_url?: string | null;
  profile_jersey_number?: number;
  naturality?: string;
  height_cm?: number;
  weight_kg?: number;
  first_seen_season_id?: number;
  last_seen_season_id?: number;
}

export interface Game {
  id: number;
  game_date?: string;
  date?: string;
  season_id?: number;
  home_team_id?: number;
  away_team_id?: number;
  home_score?: number;
  away_score?: number;
  home_team_name?: string;
  away_team_name?: string;
  phase?: string;
  stage?: string;
  round?: string;
  arena?: string;
  venue?: string;
  city?: string;
  state?: string;
  boxscore_url?: string;
  source_url?: string;
}

export interface Standing {
  id: number;
  season_id: number;
  team_id: number;
  team_name: string;
  rank: number;
  position?: number;
  wins: number;
  losses: number;
  pct: number;
  ap_pct?: number;
  point_diff?: number;
  points_for?: number;
  points_against?: number;
  points_difference?: number;
  is_champion?: number;
}

export interface PlayerGameStats {
  id: number;
  player_id: number;
  team_id: number;
  opponent_team_id: number;
  game_id: number;
  season_id: number;
  points?: number;
  rebounds?: number;
  assists?: number;
  steals?: number;
  blocks?: number;
  efficiency?: number;
  minutes?: string;
  turnovers?: number;
  fouls_committed?: number;
  [key: string]: any;
}
