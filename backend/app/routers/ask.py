from typing import Annotated, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.ask_service import answer_question
from app.database import get_db

router = APIRouter(prefix="/ask", tags=["ask"])


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Pergunta em linguagem natural.")


@router.post("")
def ask_question(
    payload: AskRequest,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    return answer_question(db, payload.question)


@router.get("/examples")
def ask_examples() -> dict[str, list[str]]:
    return {
        "examples": [
            "matheusinho ultimos 5 jogos",
            "matheusinho vs teichmann ultimos 5 jogos",
            "top 3 jogos com mais pontos do matheusinho",
            "top 3 jogos com mais rebotes do matheusinho",
            "top 10 pontos",
            "top 10 rebotes",
            "top 10 times com mais vitorias na historia",
            "lucas ultimos 5 jogos",
        ]
    }


@router.get("/intents")
def ask_intents() -> dict[str, Any]:
    return {
        "intents": [
            {
                "name": "player_recent_games",
                "description": "Retorna os últimos N jogos de um jogador com todas as colunas disponíveis de player_game_stats.",
            },
            {
                "name": "player_top_games",
                "description": "Retorna os top N jogos de um jogador por uma métrica, usando player_game_stats.",
            },
            {
                "name": "players_head_to_head_recent_games",
                "description": "Retorna os últimos N confrontos diretos entre dois jogadores, com as linhas dos dois no mesmo game_id.",
            },
            {
                "name": "team_history_ranking",
                "description": "Retorna ranking histórico de times somando team_seasons por team_id.",
            },
            {
                "name": "ranking",
                "description": "Retorna rankings simples. Para jogadores sem temporada, usa player_career_totals por padrão.",
            },
        ],
        "important_decision": "O endpoint /ask não resume estatísticas individuais. Para jogos de jogador, ele retorna tudo que existe na linha de player_game_stats, incluindo colunas contextuais de jogo, time e jogador.",
    }