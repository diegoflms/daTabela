from dataclasses import dataclass


@dataclass(frozen=True)
class MetricSpec:
    key: str
    label: str
    column_candidates: tuple[str, ...]
    higher_is_better: bool = True


PLAYER_METRICS: tuple[MetricSpec, ...] = (
    MetricSpec("points", "Pontos", ("points", "pts", "total_points", "points_total", "pts_total")),
    MetricSpec("points_per_game", "Pontos por jogo", ("points_per_game", "ppg", "pts_per_game", "avg_points", "points_avg", "pts_avg")),
    MetricSpec("rebounds", "Rebotes", ("rebounds", "reb", "total_rebounds", "rebounds_total", "trb")),
    MetricSpec("rebounds_per_game", "Rebotes por jogo", ("rebounds_per_game", "rpg", "reb_per_game", "avg_rebounds")),
    MetricSpec("assists", "Assistências", ("assists", "ast", "total_assists", "assists_total")),
    MetricSpec("assists_per_game", "Assistências por jogo", ("assists_per_game", "apg", "ast_per_game", "avg_assists")),
    MetricSpec("steals", "Roubos", ("steals", "stl", "total_steals", "steals_total")),
    MetricSpec("steals_per_game", "Roubos por jogo", ("steals_per_game", "spg", "stl_per_game", "avg_steals")),
    MetricSpec("blocks", "Tocos", ("blocks", "blk", "total_blocks", "blocks_total")),
    MetricSpec("blocks_per_game", "Tocos por jogo", ("blocks_per_game", "bpg", "blk_per_game", "avg_blocks")),
    MetricSpec("efficiency", "Eficiência", ("efficiency", "eff", "total_efficiency", "efficiency_total")),
    MetricSpec("efficiency_per_game", "Eficiência por jogo", ("efficiency_per_game", "eff_per_game", "avg_efficiency")),
    MetricSpec("minutes", "Minutos", ("minutes", "min", "minutes_played", "total_minutes")),
    MetricSpec("games", "Jogos", ("games", "games_played", "gp")),
)

TEAM_METRICS: tuple[MetricSpec, ...] = (
    MetricSpec("wins", "Vitórias", ("wins", "w")),
    MetricSpec("losses", "Derrotas", ("losses", "l")),
    MetricSpec("points", "Pontos marcados", ("points", "pts", "points_for", "pf", "total_points")),
    MetricSpec("points_per_game", "Pontos marcados por jogo", ("points_per_game", "ppg", "points_for_per_game", "pf_per_game")),
    MetricSpec("points_against", "Pontos sofridos", ("points_against", "pa", "points_allowed", "total_points_against")),
    MetricSpec("rebounds", "Rebotes", ("rebounds", "reb", "total_rebounds")),
    MetricSpec("rebounds_per_game", "Rebotes por jogo", ("rebounds_per_game", "rpg", "reb_per_game", "avg_rebounds")),
    MetricSpec("assists", "Assistências", ("assists", "ast", "total_assists")),
    MetricSpec("assists_per_game", "Assistências por jogo", ("assists_per_game", "apg", "ast_per_game", "avg_assists")),
    MetricSpec("steals", "Roubos", ("steals", "stl", "total_steals")),
    MetricSpec("steals_per_game", "Roubos por jogo", ("steals_per_game", "spg", "stl_per_game", "avg_steals")),
    MetricSpec("blocks", "Tocos", ("blocks", "blk", "total_blocks")),
    MetricSpec("blocks_per_game", "Tocos por jogo", ("blocks_per_game", "bpg", "blk_per_game", "avg_blocks")),
    MetricSpec("efficiency", "Eficiência", ("efficiency", "eff", "total_efficiency")),
    MetricSpec("efficiency_per_game", "Eficiência por jogo", ("efficiency_per_game", "eff_per_game", "avg_efficiency")),
    MetricSpec("games", "Jogos", ("games", "games_played", "gp")),
)

GAMES_COLUMN_CANDIDATES = ("games", "games_played", "gp")