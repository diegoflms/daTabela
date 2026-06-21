import re
import unicodedata
from dataclasses import dataclass
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.ranking_service import rank_table_by_metric
from app.repositories import get_table_columns, table_exists
from app.schema import quote_identifier


DEFAULT_RECENT_GAMES = 5
MAX_RECENT_GAMES = 50


@dataclass(frozen=True)
class ParsedQuestion:
    intent: str
    player_queries: tuple[str, ...] = ()
    last_n_games: int = DEFAULT_RECENT_GAMES
    ranking_target: str | None = None
    ranking_metric: str | None = None
    top_n: int = 10


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        char
        for char in normalized
        if not unicodedata.combining(char)
    )

    return re.sub(r"\s+", " ", without_accents.lower()).strip()


def _existing_columns(
    db: Session,
    table_name: str,
    candidates: tuple[str, ...],
) -> list[str]:
    if not table_exists(db, table_name):
        return []

    columns = get_table_columns(db, table_name)

    return [column for column in candidates if column in columns]


def _first_existing_column(
    db: Session,
    table_name: str,
    candidates: tuple[str, ...],
) -> str | None:
    existing = _existing_columns(db, table_name, candidates)

    if not existing:
        return None

    return existing[0]


def _metric_from_text(text_value: str) -> str | None:
    normalized = normalize_text(text_value)

    aliases = {
        "pontos": "points",
        "ponto": "points",
        "pts": "points",
        "pontuacao": "points",
        "pontuação": "points",
        "rebotes": "rebounds",
        "rebote": "rebounds",
        "reb": "rebounds",
        "assistencias": "assists",
        "assistências": "assists",
        "assistencia": "assists",
        "assistência": "assists",
        "ast": "assists",
        "roubos": "steals",
        "roubo": "steals",
        "stl": "steals",
        "tocos": "blocks",
        "toco": "blocks",
        "blocks": "blocks",
        "blk": "blocks",
        "eficiencia": "efficiency",
        "eficiência": "efficiency",
        "eff": "efficiency",
        "minutos": "minutes",
        "minuto": "minutes",
        "min": "minutes",
        "enterradas": "dunks",
        "enterrada": "dunks",
        "dunks": "dunks",
        "cravadas": "dunks",
        "cravada": "dunks",
        "turnovers": "turnovers",
        "erros": "turnovers",
        "faltas": "fouls_committed",
        "jogos": "games",
        "partidas": "games",
        "vitorias": "wins",
        "vitórias": "wins",
        "derrotas": "losses",
    }

    for alias in sorted(aliases, key=len, reverse=True):
        if re.search(rf"\b{re.escape(alias)}\b", normalized):
            return aliases[alias]

    return None


def _metric_candidates(metric_key: str, *, career: bool = False) -> tuple[str, ...]:
    if career:
        mapping = {
            "points": ("points_total", "total_points", "pts_total", "points", "pts"),
            "rebounds": ("rebounds_total", "total_rebounds", "rebounds", "reb", "trb"),
            "assists": ("assists_total", "total_assists", "assists", "ast"),
            "steals": ("steals_total", "total_steals", "steals", "stl"),
            "blocks": ("blocks_total", "total_blocks", "blocks", "blk"),
            "efficiency": ("efficiency_total", "total_efficiency", "efficiency", "eff"),
            "minutes": ("minutes_total", "total_minutes", "minutes", "min", "minutes_played"),
            "dunks": ("dunks_total", "total_dunks", "dunks", "dunk"),
            "turnovers": ("turnovers_total", "total_turnovers", "turnovers", "tov"),
            "fouls_committed": ("fouls_committed_total", "total_fouls_committed", "fouls_committed"),
            "games": ("games_played", "games", "gp"),
            "wins": ("wins", "w"),
            "losses": ("losses", "l"),
        }
    else:
        mapping = {
            "points": ("points", "pts", "points_total", "total_points", "pts_total"),
            "rebounds": ("rebounds", "reb", "total_rebounds", "rebounds_total", "trb"),
            "assists": ("assists", "ast", "total_assists", "assists_total"),
            "steals": ("steals", "stl", "total_steals", "steals_total"),
            "blocks": ("blocks", "blk", "total_blocks", "blocks_total"),
            "efficiency": ("efficiency", "eff", "total_efficiency", "efficiency_total"),
            "minutes": ("minutes", "min", "minutes_played", "total_minutes"),
            "dunks": ("dunks", "dunk", "dunks_total", "total_dunks"),
            "turnovers": ("turnovers", "tov", "turnovers_total", "total_turnovers"),
            "fouls_committed": ("fouls_committed", "fouls_committed_total", "total_fouls_committed"),
            "games": ("games", "games_played", "gp"),
            "wins": ("wins", "w"),
            "losses": ("losses", "l"),
        }

    return mapping.get(metric_key, (metric_key,))


def _resolve_metric_column(
    db: Session,
    table_name: str,
    metric_key: str,
    *,
    career: bool = False,
) -> str | None:
    if not table_exists(db, table_name):
        return None

    columns = get_table_columns(db, table_name)

    for candidate in _metric_candidates(metric_key, career=career):
        if candidate in columns:
            return candidate

    return None


def _remove_recent_games_fragment(question: str) -> str:
    return re.sub(
        r"\b(ultimos|últimos|ultimas|últimas|last)\s+\d+\s+(jogos|games|partidas)\b",
        "",
        question,
        flags=re.IGNORECASE,
    ).strip()


def _extract_last_n_games(question: str) -> int:
    normalized = normalize_text(question)

    match = re.search(r"\b(?:ultimos|ultimas|last)\s+(\d+)\s+(?:jogos|games|partidas)\b", normalized)

    if not match:
        return DEFAULT_RECENT_GAMES

    value = int(match.group(1))

    return max(1, min(value, MAX_RECENT_GAMES))


def _parse_top_player_games_question(question: str) -> ParsedQuestion | None:
    normalized = normalize_text(question)

    patterns = (
        r"\btop\s+(\d+)\s+jogos\s+com\s+mais\s+(.+?)\s+d[oea]\s+(.+)$",
        r"\btop\s+(\d+)\s+partidas\s+com\s+mais\s+(.+?)\s+d[oea]\s+(.+)$",
        r"\btop\s+(\d+)\s+jogos\s+d[oea]\s+(.+?)\s+com\s+mais\s+(.+)$",
        r"\btop\s+(\d+)\s+partidas\s+d[oea]\s+(.+?)\s+com\s+mais\s+(.+)$",
    )

    for pattern_index, pattern in enumerate(patterns):
        match = re.search(pattern, normalized)

        if not match:
            continue

        top_n = max(1, min(int(match.group(1)), MAX_RECENT_GAMES))

        if pattern_index < 2:
            metric_text = match.group(2).strip()
            player_query = match.group(3).strip()
        else:
            player_query = match.group(2).strip()
            metric_text = match.group(3).strip()

        metric = _metric_from_text(metric_text)

        if not metric or not player_query:
            return None

        return ParsedQuestion(
            intent="player_top_games",
            player_queries=(player_query,),
            ranking_metric=metric,
            top_n=top_n,
        )

    return None


def _parse_top_question(question: str) -> ParsedQuestion | None:
    top_player_games = _parse_top_player_games_question(question)

    if top_player_games is not None:
        return top_player_games

    normalized = normalize_text(question)

    match = re.search(r"\btop\s+(\d+)\s+(.+)", normalized)

    if not match:
        return None

    top_n = max(1, min(int(match.group(1)), 200))
    metric_text = match.group(2).strip()

    target = "players"

    if "time" in metric_text or "times" in metric_text or "equipes" in metric_text:
        target = "teams"

    history_words = ("historia", "historico", "carreira", "todos os tempos")
    is_history = any(word in metric_text for word in history_words)

    metric = _metric_from_text(metric_text)

    if metric and target == "teams" and is_history:
        return ParsedQuestion(
            intent="team_history_ranking",
            ranking_target="teams",
            ranking_metric=metric,
            top_n=top_n,
        )

    if metric:
        return ParsedQuestion(
            intent="ranking",
            ranking_target=target,
            ranking_metric=metric,
            top_n=top_n,
        )

    return ParsedQuestion(intent="unknown")


def parse_question(question: str) -> ParsedQuestion:
    top_question = _parse_top_question(question)

    if top_question is not None:
        return top_question

    last_n_games = _extract_last_n_games(question)
    without_recent = _remove_recent_games_fragment(question)
    normalized_without_recent = normalize_text(without_recent)

    separators = (" vs ", " versus ", " contra ")

    for separator in separators:
        if separator.strip() in normalized_without_recent:
            left, right = normalized_without_recent.split(separator.strip(), 1)
            left = left.strip(" ,.;:-")
            right = right.strip(" ,.;:-")

            if left and right:
                return ParsedQuestion(
                    intent="players_head_to_head_recent_games",
                    player_queries=(left, right),
                    last_n_games=last_n_games,
                )

    cleaned = normalized_without_recent.strip(" ,.;:-")

    prefixes = (
        "jogos de ",
        "jogos do ",
        "jogos da ",
        "estatisticas de ",
        "estatísticas de ",
        "stats de ",
        "ultimos jogos de ",
        "últimos jogos de ",
    )

    for prefix in prefixes:
        normalized_prefix = normalize_text(prefix)

        if cleaned.startswith(normalized_prefix):
            cleaned = cleaned[len(normalized_prefix):].strip()

    if cleaned:
        return ParsedQuestion(
            intent="player_recent_games",
            player_queries=(cleaned,),
            last_n_games=last_n_games,
        )

    return ParsedQuestion(intent="unknown")


def _player_display_name(row: dict[str, Any]) -> str:
    for column in ("name", "full_name", "display_name", "player_name", "nickname", "slug", "matched_value"):
        value = row.get(column)

        if value:
            return str(value)

    return f"player_id={row.get('id') or row.get('player_id')}"


def _row_key(row: dict[str, Any]) -> Any:
    return row.get("id") or row.get("player_id")


def _search_players_table(
    db: Session,
    query: str,
    *,
    limit: int,
) -> list[dict[str, Any]]:
    search_columns = _existing_columns(
        db,
        "players",
        ("name", "full_name", "display_name", "player_name", "nickname", "slug"),
    )

    if not search_columns:
        return []

    where_sql = " OR ".join(
        f"LOWER(CAST({quote_identifier(column)} AS TEXT)) LIKE LOWER(:query)"
        for column in search_columns
    )

    order_column = _first_existing_column(
        db,
        "players",
        ("name", "full_name", "display_name", "player_name", "nickname", "slug", "id"),
    ) or "id"

    statement = text(
        f"""
        SELECT *
        FROM "players"
        WHERE {where_sql}
        ORDER BY {quote_identifier(order_column)}
        LIMIT :limit
        """
    )

    rows = [
        dict(row)
        for row in db.execute(
            statement,
            {"query": f"%{query}%", "limit": limit},
        ).mappings().all()
    ]

    for row in rows:
        row["matched_via"] = "players"
        row["matched_value"] = _player_display_name(row)

    return rows


def _search_player_aliases_table(
    db: Session,
    query: str,
    *,
    limit: int,
) -> list[dict[str, Any]]:
    if not table_exists(db, "player_aliases"):
        return []

    alias_columns = _existing_columns(
        db,
        "player_aliases",
        ("alias", "name", "raw_name", "player_name", "full_name", "nickname", "slug"),
    )

    alias_table_columns = get_table_columns(db, "player_aliases")

    if "player_id" not in alias_table_columns or not alias_columns:
        return []

    player_table_exists = table_exists(db, "players")
    player_columns = get_table_columns(db, "players") if player_table_exists else set()

    player_select = "p.*" if player_table_exists else 'a."player_id" AS id'
    join_sql = 'LEFT JOIN "players" AS p ON p."id" = a."player_id"' if player_table_exists else ""

    if len(alias_columns) == 1:
        matched_expr = f'a.{quote_identifier(alias_columns[0])}'
    else:
        matched_expr = "COALESCE(" + ", ".join(f'a.{quote_identifier(column)}' for column in alias_columns) + ")"

    where_sql = " OR ".join(
        f"LOWER(CAST(a.{quote_identifier(column)} AS TEXT)) LIKE LOWER(:query)"
        for column in alias_columns
    )

    order_expr = 'a."player_id"'

    for candidate in ("name", "full_name", "player_name", "slug"):
        if candidate in player_columns:
            order_expr = f'p.{quote_identifier(candidate)}'
            break

    statement = text(
        f"""
        SELECT
            {player_select},
            'player_aliases' AS matched_via,
            {matched_expr} AS matched_value
        FROM "player_aliases" AS a
        {join_sql}
        WHERE {where_sql}
        ORDER BY {order_expr}
        LIMIT :limit
        """
    )

    return [
        dict(row)
        for row in db.execute(
            statement,
            {"query": f"%{query}%", "limit": limit},
        ).mappings().all()
    ]


def resolve_player_candidates(
    db: Session,
    query: str,
    *,
    limit: int = 10,
) -> list[dict[str, Any]]:
    players_rows = _search_players_table(db, query, limit=limit)
    alias_rows = _search_player_aliases_table(db, query, limit=limit)

    merged: list[dict[str, Any]] = []
    seen_ids: set[Any] = set()

    for row in players_rows + alias_rows:
        key = _row_key(row)

        if key in seen_ids:
            continue

        seen_ids.add(key)
        merged.append(row)

        if len(merged) >= limit:
            break

    return merged


def _candidate_texts(candidate: dict[str, Any]) -> set[str]:
    texts: set[str] = set()

    for column in ("name", "full_name", "display_name", "player_name", "nickname", "slug", "matched_value"):
        value = candidate.get(column)

        if value:
            texts.add(normalize_text(str(value)))

    return texts


def resolve_single_player(
    db: Session,
    query: str,
) -> dict[str, Any]:
    candidates = resolve_player_candidates(db, query, limit=10)

    if not candidates:
        return {
            "status": "not_found",
            "query": query,
            "player": None,
            "candidates": [],
        }

    normalized_query = normalize_text(query)
    tokens = normalized_query.split()
    is_short_single_name = len(tokens) == 1 and len(normalized_query) <= 6

    if is_short_single_name and len(candidates) > 1:
        return {
            "status": "ambiguous",
            "query": query,
            "player": None,
            "candidates": candidates,
        }

    exact_alias_candidates = [
        candidate
        for candidate in candidates
        if candidate.get("matched_via") == "player_aliases"
        and normalize_text(str(candidate.get("matched_value", ""))) == normalized_query
    ]

    if len(exact_alias_candidates) == 1:
        return {
            "status": "ok",
            "query": query,
            "player": exact_alias_candidates[0],
            "candidates": candidates,
        }

    exact_candidates = [
        candidate
        for candidate in candidates
        if normalized_query in _candidate_texts(candidate)
    ]

    if len(exact_candidates) == 1:
        return {
            "status": "ok",
            "query": query,
            "player": exact_candidates[0],
            "candidates": candidates,
        }

    if len(candidates) == 1:
        return {
            "status": "ok",
            "query": query,
            "player": candidates[0],
            "candidates": candidates,
        }

    return {
        "status": "ambiguous",
        "query": query,
        "player": None,
        "candidates": candidates,
    }


def _build_context_selects(
    db: Session,
    base_columns: set[str],
) -> tuple[str, list[str]]:
    joins: list[str] = []
    selects: list[str] = []

    if "player_id" in base_columns and table_exists(db, "players"):
        player_columns = get_table_columns(db, "players")
        joins.append('LEFT JOIN "players" AS p ON p."id" = base."player_id"')

        for column in ("name", "full_name", "player_name", "display_name", "slug"):
            if column in player_columns:
                selects.append(f'p.{quote_identifier(column)} AS entity_player_name')
                break

        if "slug" in player_columns:
            selects.append('p."slug" AS entity_player_slug')

    if "team_id" in base_columns and table_exists(db, "teams"):
        team_columns = get_table_columns(db, "teams")
        joins.append('LEFT JOIN "teams" AS t ON t."id" = base."team_id"')

        for column in ("name", "full_name", "team_name", "display_name", "slug"):
            if column in team_columns:
                selects.append(f't.{quote_identifier(column)} AS entity_team_name')
                break

        if "slug" in team_columns:
            selects.append('t."slug" AS entity_team_slug')

    if "opponent_team_id" in base_columns and table_exists(db, "teams"):
        team_columns = get_table_columns(db, "teams")
        joins.append('LEFT JOIN "teams" AS ot ON ot."id" = base."opponent_team_id"')

        for column in ("name", "full_name", "team_name", "display_name", "slug"):
            if column in team_columns:
                selects.append(f'ot.{quote_identifier(column)} AS entity_opponent_team_name')
                break

        if "slug" in team_columns:
            selects.append('ot."slug" AS entity_opponent_team_slug')

    if "game_id" in base_columns and table_exists(db, "games"):
        game_columns = get_table_columns(db, "games")
        joins.append('LEFT JOIN "games" AS g ON g."id" = base."game_id"')

        for column in ("game_date", "date", "season_id", "home_team_id", "away_team_id", "home_score", "away_score", "phase", "stage", "round", "arena", "venue", "boxscore_url", "source_url"):
            if column in game_columns:
                selects.append(f'g.{quote_identifier(column)} AS game_{column}')

    return " ".join(joins), selects


def _resolve_game_order_column(db: Session, *, alias: str = "g", fallback_alias: str = "base") -> str:
    if not table_exists(db, "games"):
        return f'{fallback_alias}."game_id"'

    game_columns = get_table_columns(db, "games")

    for column in ("game_date", "date", "id"):
        if column in game_columns:
            return f'{alias}.{quote_identifier(column)}'

    return f'{fallback_alias}."game_id"'


def _rows_to_table(rows: list[dict[str, Any]]) -> dict[str, Any]:
    columns: list[str] = []

    for row in rows:
        for column in row.keys():
            if column not in columns:
                columns.append(column)

    return {
        "columns": columns,
        "rows": rows,
        "total": len(rows),
    }


def get_recent_player_games(
    db: Session,
    player_id: int,
    *,
    last_n_games: int,
) -> dict[str, Any]:
    last_n_games = max(1, min(last_n_games, MAX_RECENT_GAMES))

    if not table_exists(db, "player_game_stats"):
        return {"columns": [], "rows": [], "total": 0}

    base_columns = get_table_columns(db, "player_game_stats")

    if "player_id" not in base_columns:
        return {"columns": [], "rows": [], "total": 0}

    joins, context_selects = _build_context_selects(db, base_columns)
    order_column = _resolve_game_order_column(db)
    context_sql = ", " + ", ".join(context_selects) if context_selects else ""

    statement = text(
        f"""
        SELECT
            base.*
            {context_sql}
        FROM "player_game_stats" AS base
        {joins}
        WHERE base."player_id" = :player_id
        ORDER BY {order_column} DESC
        LIMIT :limit
        """
    )

    rows = [
        dict(row)
        for row in db.execute(
            statement,
            {"player_id": player_id, "limit": last_n_games},
        ).mappings().all()
    ]

    return _rows_to_table(rows)


def get_top_player_games(
    db: Session,
    player_id: int,
    *,
    metric_key: str,
    top_n: int,
) -> dict[str, Any]:
    top_n = max(1, min(top_n, MAX_RECENT_GAMES))

    if not table_exists(db, "player_game_stats"):
        return {"status": "missing_table", "metric_column": None, "columns": [], "rows": [], "total": 0}

    base_columns = get_table_columns(db, "player_game_stats")

    if "player_id" not in base_columns:
        return {"status": "missing_player_id", "metric_column": None, "columns": [], "rows": [], "total": 0}

    metric_column = _resolve_metric_column(db, "player_game_stats", metric_key, career=False)

    if metric_column is None:
        return {
            "status": "missing_metric",
            "metric_column": None,
            "available_columns": sorted(base_columns),
            "columns": [],
            "rows": [],
            "total": 0,
        }

    joins, context_selects = _build_context_selects(db, base_columns)
    context_sql = ", " + ", ".join(context_selects) if context_selects else ""

    statement = text(
        f"""
        SELECT
            base.*,
            CAST(base.{quote_identifier(metric_column)} AS REAL) AS ranking_value
            {context_sql}
        FROM "player_game_stats" AS base
        {joins}
        WHERE base."player_id" = :player_id
          AND base.{quote_identifier(metric_column)} IS NOT NULL
          AND base.{quote_identifier(metric_column)} != ''
        ORDER BY ranking_value DESC
        LIMIT :limit
        """
    )

    rows = [
        dict(row)
        for row in db.execute(
            statement,
            {"player_id": player_id, "limit": top_n},
        ).mappings().all()
    ]

    table = _rows_to_table(rows)
    table["status"] = "ok"
    table["metric_column"] = metric_column
    return table


def get_players_head_to_head_games(
    db: Session,
    player1_id: int,
    player2_id: int,
    *,
    last_n_games: int,
) -> dict[str, Any]:
    last_n_games = max(1, min(last_n_games, MAX_RECENT_GAMES))

    if not table_exists(db, "player_game_stats"):
        return {"columns": [], "rows": [], "total": 0, "games_count": 0}

    base_columns = get_table_columns(db, "player_game_stats")

    if "player_id" not in base_columns or "game_id" not in base_columns:
        return {"columns": [], "rows": [], "total": 0, "games_count": 0}

    has_team_id = "team_id" in base_columns
    team_condition = ""

    if has_team_id:
        team_condition = 'AND (p1."team_id" IS NULL OR p2."team_id" IS NULL OR p1."team_id" != p2."team_id")'

    cte_game_join = ""
    order_expr = 'p1."game_id"'

    if table_exists(db, "games"):
        game_columns = get_table_columns(db, "games")
        cte_game_join = 'LEFT JOIN "games" AS gg ON gg."id" = p1."game_id"'

        for column in ("game_date", "date", "id"):
            if column in game_columns:
                order_expr = f'gg.{quote_identifier(column)}'
                break

    joins, context_selects = _build_context_selects(db, base_columns)
    context_sql = ", " + ", ".join(context_selects) if context_selects else ""

    statement = text(
        f"""
        WITH h2h_games AS (
            SELECT
                p1."game_id" AS game_id,
                {order_expr} AS order_value
            FROM "player_game_stats" AS p1
            JOIN "player_game_stats" AS p2
              ON p2."game_id" = p1."game_id"
            {cte_game_join}
            WHERE p1."player_id" = :player1_id
              AND p2."player_id" = :player2_id
              {team_condition}
            GROUP BY p1."game_id"
            ORDER BY order_value DESC
            LIMIT :limit
        )
        SELECT
            base.*,
            CAST(h2h_games.order_value AS TEXT) AS h2h_order_value
            {context_sql}
        FROM "player_game_stats" AS base
        JOIN h2h_games
          ON h2h_games.game_id = base."game_id"
        {joins}
        WHERE base."player_id" IN (:player1_id, :player2_id)
        ORDER BY h2h_games.order_value DESC, base."game_id", base."player_id"
        """
    )

    rows = [
        dict(row)
        for row in db.execute(
            statement,
            {
                "player1_id": player1_id,
                "player2_id": player2_id,
                "limit": last_n_games,
            },
        ).mappings().all()
    ]

    table = _rows_to_table(rows)
    table["games_count"] = len({row.get("game_id") for row in rows if row.get("game_id") is not None})
    return table


def _build_player_recent_response(
    db: Session,
    question: str,
    parsed: ParsedQuestion,
) -> dict[str, Any]:
    query = parsed.player_queries[0]
    resolved = resolve_single_player(db, query)

    if resolved["status"] == "not_found":
        return {
            "status": "not_found",
            "question": question,
            "message": "Não encontrei jogador compatível com a pergunta.",
            "interpreted_as": {"intent": parsed.intent, "player_query": query, "last_n_games": parsed.last_n_games},
            "candidates": [],
            "columns": [],
            "rows": [],
        }

    if resolved["status"] == "ambiguous":
        return {
            "status": "needs_clarification",
            "question": question,
            "message": "Encontrei mais de um jogador possível. Escolha um candidato.",
            "interpreted_as": {"intent": parsed.intent, "player_query": query, "last_n_games": parsed.last_n_games},
            "candidates": resolved["candidates"],
            "columns": [],
            "rows": [],
        }

    player = resolved["player"]
    player_id = int(_row_key(player))
    table = get_recent_player_games(db, player_id, last_n_games=parsed.last_n_games)

    return {
        "status": "ok",
        "question": question,
        "title": f"{_player_display_name(player)} - últimos {parsed.last_n_games} jogos",
        "interpreted_as": {
            "intent": parsed.intent,
            "player": {"id": player_id, "name": _player_display_name(player), "matched_via": player.get("matched_via"), "matched_value": player.get("matched_value")},
            "last_n_games": parsed.last_n_games,
        },
        "source_tables": ["player_game_stats", "players", "player_aliases", "games", "teams"],
        "columns": table["columns"],
        "rows": table["rows"],
        "total": table["total"],
    }


def _build_player_top_games_response(
    db: Session,
    question: str,
    parsed: ParsedQuestion,
) -> dict[str, Any]:
    query = parsed.player_queries[0]
    resolved = resolve_single_player(db, query)

    if resolved["status"] == "not_found":
        return {
            "status": "not_found",
            "question": question,
            "message": "Não encontrei jogador compatível com a pergunta.",
            "interpreted_as": {"intent": parsed.intent, "player_query": query, "metric": parsed.ranking_metric, "top_n": parsed.top_n},
            "candidates": [],
            "columns": [],
            "rows": [],
        }

    if resolved["status"] == "ambiguous":
        return {
            "status": "needs_clarification",
            "question": question,
            "message": "Encontrei mais de um jogador possível. Escolha um candidato.",
            "interpreted_as": {"intent": parsed.intent, "player_query": query, "metric": parsed.ranking_metric, "top_n": parsed.top_n},
            "candidates": resolved["candidates"],
            "columns": [],
            "rows": [],
        }

    player = resolved["player"]
    player_id = int(_row_key(player))
    metric_key = parsed.ranking_metric or "points"
    table = get_top_player_games(db, player_id, metric_key=metric_key, top_n=parsed.top_n)

    if table.get("status") != "ok":
        return {
            "status": "needs_clarification",
            "question": question,
            "message": "Não encontrei coluna compatível para essa métrica em player_game_stats.",
            "interpreted_as": {
                "intent": parsed.intent,
                "player": {"id": player_id, "name": _player_display_name(player), "matched_via": player.get("matched_via"), "matched_value": player.get("matched_value")},
                "metric": metric_key,
                "top_n": parsed.top_n,
            },
            "available_columns": table.get("available_columns", []),
            "columns": [],
            "rows": [],
        }

    return {
        "status": "ok",
        "question": question,
        "title": f"Top {parsed.top_n} jogos com mais {metric_key} de {_player_display_name(player)}",
        "interpreted_as": {
            "intent": parsed.intent,
            "player": {"id": player_id, "name": _player_display_name(player), "matched_via": player.get("matched_via"), "matched_value": player.get("matched_value")},
            "metric": metric_key,
            "metric_column": table["metric_column"],
            "top_n": parsed.top_n,
        },
        "source_tables": ["player_game_stats", "players", "player_aliases", "games", "teams"],
        "columns": table["columns"],
        "rows": table["rows"],
        "total": table["total"],
        "note": "Esta pergunta é sobre os melhores jogos de um jogador, então a fonte correta é player_game_stats, não player_career_totals.",
    }


def _resolve_two_players_or_response(
    db: Session,
    question: str,
    parsed: ParsedQuestion,
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    resolved_players: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []

    for query in parsed.player_queries:
        resolved = resolve_single_player(db, query)

        if resolved["status"] != "ok":
            unresolved.append(resolved)
        else:
            resolved_players.append(resolved["player"])

    if unresolved:
        return [], {
            "status": "needs_clarification",
            "question": question,
            "message": "Não consegui resolver todos os jogadores com segurança.",
            "interpreted_as": {"intent": parsed.intent, "player_queries": list(parsed.player_queries), "last_n_games": parsed.last_n_games},
            "unresolved": unresolved,
            "columns": [],
            "rows": [],
        }

    return resolved_players, None


def _build_players_head_to_head_response(
    db: Session,
    question: str,
    parsed: ParsedQuestion,
) -> dict[str, Any]:
    resolved_players, error_response = _resolve_two_players_or_response(db, question, parsed)

    if error_response is not None:
        return error_response

    player1, player2 = resolved_players
    player1_id = int(_row_key(player1))
    player2_id = int(_row_key(player2))

    table = get_players_head_to_head_games(
        db,
        player1_id,
        player2_id,
        last_n_games=parsed.last_n_games,
    )

    return {
        "status": "ok",
        "question": question,
        "title": f"{_player_display_name(player1)} vs {_player_display_name(player2)} - últimos {parsed.last_n_games} confrontos diretos",
        "interpreted_as": {
            "intent": parsed.intent,
            "players": [
                {"id": player1_id, "name": _player_display_name(player1), "matched_via": player1.get("matched_via"), "matched_value": player1.get("matched_value")},
                {"id": player2_id, "name": _player_display_name(player2), "matched_via": player2.get("matched_via"), "matched_value": player2.get("matched_value")},
            ],
            "last_n_head_to_head_games": parsed.last_n_games,
        },
        "source_tables": ["player_game_stats", "players", "player_aliases", "games", "teams"],
        "columns": table["columns"],
        "rows": table["rows"],
        "total": table["total"],
        "games_count": table["games_count"],
        "note": "Para perguntas com vs/contra, o /ask retorna jogos em que os dois jogadores aparecem no mesmo game_id, preferencialmente em times diferentes quando team_id existe.",
    }


def _build_ranking_response(
    db: Session,
    question: str,
    parsed: ParsedQuestion,
) -> dict[str, Any]:
    if parsed.ranking_target == "teams":
        table_name = "team_seasons"
        career = False
    else:
        table_name = "player_career_totals"
        career = True

        if not table_exists(db, table_name):
            table_name = "player_seasons"
            career = False

    metric_key = parsed.ranking_metric or "points"
    metric_column = _resolve_metric_column(db, table_name, metric_key, career=career)

    if metric_column is None:
        return {
            "status": "needs_clarification",
            "question": question,
            "message": "Não encontrei uma coluna compatível para esse ranking.",
            "interpreted_as": {"intent": parsed.intent, "target": parsed.ranking_target or "players", "metric": metric_key, "source_table": table_name},
            "available_columns": sorted(get_table_columns(db, table_name)) if table_exists(db, table_name) else [],
            "columns": [],
            "rows": [],
        }

    result = rank_table_by_metric(
        db,
        table_name,
        metric_column,
        limit=parsed.top_n,
        offset=0,
        higher_is_better=True,
    )

    return {
        "status": "ok",
        "question": question,
        "title": f"Top {parsed.top_n} - {metric_key}",
        "interpreted_as": {
            "intent": parsed.intent,
            "target": parsed.ranking_target or "players",
            "metric": metric_key,
            "metric_column": metric_column,
            "top_n": parsed.top_n,
            "source_table": table_name,
        },
        "source_tables": [table_name],
        "columns": list(result["items"][0].keys()) if result["items"] else [],
        "rows": result["items"],
        "total": result["total"],
        "limit": result["limit"],
        "offset": result["offset"],
        "note": "Para perguntas do tipo top N sem temporada, o /ask usa player_career_totals para bater com totais de carreira.",
    }


def _numeric_aggregate_columns(columns: set[str]) -> list[str]:
    excluded_exact = {"id", "team_id", "season_id"}
    excluded_fragments = ("name", "slug", "url", "date", "phase", "stage", "round", "arena", "venue", "city", "state")

    result: list[str] = []

    for column in sorted(columns):
        if column in excluded_exact:
            continue

        if any(fragment in column for fragment in excluded_fragments):
            continue

        result.append(column)

    return result


def _build_team_history_ranking_response(
    db: Session,
    question: str,
    parsed: ParsedQuestion,
) -> dict[str, Any]:
    table_name = "team_seasons"
    metric_key = parsed.ranking_metric or "wins"

    if not table_exists(db, table_name):
        return {"status": "not_found", "question": question, "message": "team_seasons não existe.", "columns": [], "rows": []}

    columns = get_table_columns(db, table_name)

    if "team_id" not in columns:
        return {"status": "needs_clarification", "question": question, "message": "team_seasons não tem team_id.", "columns": [], "rows": []}

    metric_column = _resolve_metric_column(db, table_name, metric_key, career=False)

    if metric_column is None:
        return {
            "status": "needs_clarification",
            "question": question,
            "message": "Não encontrei coluna compatível para ranking histórico de times.",
            "available_columns": sorted(columns),
            "columns": [],
            "rows": [],
        }

    aggregate_columns = _numeric_aggregate_columns(columns)

    select_parts = [
        'base."team_id" AS team_id',
        "COUNT(*) AS seasons_count",
        f'SUM(CAST(base.{quote_identifier(metric_column)} AS REAL)) AS ranking_value',
    ]

    if "season_id" in columns:
        select_parts.append('GROUP_CONCAT(base."season_id", "|") AS season_ids')

    for column in aggregate_columns:
        select_parts.append(f'SUM(CAST(base.{quote_identifier(column)} AS REAL)) AS {quote_identifier(column + "_total")}')

    join_sql = ""
    team_columns = get_table_columns(db, "teams") if table_exists(db, "teams") else set()

    if team_columns:
        join_sql = 'LEFT JOIN "teams" AS t ON t."id" = base."team_id"'

        for column in ("name", "full_name", "team_name", "display_name", "slug"):
            if column in team_columns:
                select_parts.insert(1, f't.{quote_identifier(column)} AS team_name')
                break

        if "slug" in team_columns:
            select_parts.insert(2, 't."slug" AS team_slug')

    statement = text(
        f"""
        SELECT
            {", ".join(select_parts)}
        FROM "team_seasons" AS base
        {join_sql}
        GROUP BY base."team_id"
        ORDER BY ranking_value DESC
        LIMIT :limit
        """
    )

    rows = [
        dict(row)
        for row in db.execute(statement, {"limit": parsed.top_n}).mappings().all()
    ]

    table = _rows_to_table(rows)

    return {
        "status": "ok",
        "question": question,
        "title": f"Top {parsed.top_n} times históricos por {metric_key}",
        "interpreted_as": {
            "intent": parsed.intent,
            "target": "teams",
            "metric": metric_key,
            "metric_column": metric_column,
            "top_n": parsed.top_n,
            "source_table": table_name,
            "aggregation": "SUM por team_id",
        },
        "source_tables": ["team_seasons", "teams"],
        "columns": table["columns"],
        "rows": table["rows"],
        "total": table["total"],
        "note": "Para ranking histórico de times, o /ask soma team_seasons por team_id. Assim não retorna uma temporada isolada como se fosse ranking histórico.",
    }


def answer_question(db: Session, question: str) -> dict[str, Any]:
    parsed = parse_question(question)

    if parsed.intent == "player_top_games":
        return _build_player_top_games_response(db, question, parsed)

    if parsed.intent == "players_head_to_head_recent_games":
        return _build_players_head_to_head_response(db, question, parsed)

    if parsed.intent == "player_recent_games":
        return _build_player_recent_response(db, question, parsed)

    if parsed.intent == "team_history_ranking":
        return _build_team_history_ranking_response(db, question, parsed)

    if parsed.intent == "ranking":
        return _build_ranking_response(db, question, parsed)

    return {
        "status": "unsupported",
        "question": question,
        "message": "Ainda não sei interpretar essa pergunta no MVP.",
        "supported_examples": [
            "matheusinho ultimos 5 jogos",
            "matheusinho vs teichmann ultimos 5 jogos",
            "top 3 jogos com mais pontos do matheusinho",
            "top 10 pontos",
            "top 10 rebotes",
            "top 10 times com mais vitorias na historia",
        ],
        "columns": [],
        "rows": [],
    }