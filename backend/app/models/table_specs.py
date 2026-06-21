from dataclasses import dataclass


@dataclass(frozen=True)
class TableSpec:
    """Contrato de uma tabela final importada dos CSVs."""

    table_name: str
    csv_file: str
    description: str
    primary_key: str | None = "id"
    index_columns: tuple[str, ...] = ()


FINAL_TABLE_SPECS: tuple[TableSpec, ...] = (
    TableSpec(
        table_name="seasons",
        csv_file="seasons.csv",
        description="Temporadas cadastradas manualmente.",
        index_columns=("slug", "is_current"),
    ),
    TableSpec(
        table_name="teams",
        csv_file="teams.csv",
        description="Times consolidados.",
        index_columns=("slug", "name"),
    ),
    TableSpec(
        table_name="team_aliases",
        csv_file="team_aliases.csv",
        description="Aliases de times por temporada e nome cru.",
        index_columns=("team_id", "season_id", "alias", "name", "slug"),
    ),
    TableSpec(
        table_name="players",
        csv_file="players.csv",
        description="Jogadores consolidados.",
        index_columns=("slug", "name"),
    ),
    TableSpec(
        table_name="player_aliases",
        csv_file="player_aliases.csv",
        description="Aliases de jogadores por temporada, time, nome cru e camisa.",
        index_columns=("player_id", "season_id", "team_id", "alias", "name", "jersey_number"),
    ),
    TableSpec(
        table_name="games",
        csv_file="games.csv",
        description="Jogos, placares, fases, times e URLs de origem.",
        index_columns=("season_id", "home_team_id", "away_team_id", "game_date", "date", "boxscore_url"),
    ),
    TableSpec(
        table_name="player_game_stats",
        csv_file="player_game_stats.csv",
        description="Estatísticas individuais por jogador em cada jogo.",
        index_columns=("player_id", "team_id", "opponent_team_id", "game_id", "season_id"),
    ),
    TableSpec(
        table_name="team_game_stats",
        csv_file="team_game_stats.csv",
        description="Estatísticas agregadas de time por jogo.",
        index_columns=("team_id", "opponent_team_id", "game_id", "season_id"),
    ),
    TableSpec(
        table_name="standings",
        csv_file="standings.csv",
        description="Classificação por temporada derivada dos jogos.",
        index_columns=("season_id", "team_id", "rank", "is_champion"),
    ),
    TableSpec(
        table_name="team_seasons",
        csv_file="team_seasons.csv",
        description="Agregados de time por temporada.",
        index_columns=("season_id", "team_id"),
    ),
    TableSpec(
        table_name="player_team_seasons",
        csv_file="player_team_seasons.csv",
        description="Agregados de jogador por time e temporada.",
        index_columns=("player_id", "team_id", "season_id"),
    ),
    TableSpec(
        table_name="player_seasons",
        csv_file="player_seasons.csv",
        description="Agregados de jogador por temporada.",
        index_columns=("player_id", "season_id"),
    ),
    TableSpec(
        table_name="player_career_totals",
        csv_file="player_career_totals.csv",
        description="Totais e médias de carreira por jogador.",
        index_columns=("player_id",),
    ),
    TableSpec(
        table_name="player_records",
        csv_file="player_records.csv",
        description="Recordes individuais por jogador.",
        index_columns=("player_id", "season_id", "game_id", "record_type"),
    ),
    TableSpec(
        table_name="awards",
        csv_file="awards.csv",
        description="Prêmios individuais preenchidos manualmente.",
        index_columns=("season_id", "player_id", "team_id", "award_type"),
    ),
    TableSpec(
        table_name="team_titles",
        csv_file="team_titles.csv",
        description="Títulos de times preenchidos manualmente ou conferidos por standings.",
        index_columns=("season_id", "team_id", "title_type"),
    ),
)


def get_table_spec(table_name: str) -> TableSpec:
    for spec in FINAL_TABLE_SPECS:
        if spec.table_name == table_name:
            return spec

    raise KeyError(f"Tabela não cadastrada: {table_name}")