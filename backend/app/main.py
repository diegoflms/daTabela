from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import check_database_connection, engine
from app.importer import get_table_counts
from app.models.table_specs import FINAL_TABLE_SPECS
from app.routers import ask, games, players, rankings, search, seasons, standings, teams

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API do DaTabela para consulta de dados históricos e estatísticos do NBB.",
)

# Configuração de CORS para permitir requisições locais do frontend de qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(seasons.router)
app.include_router(teams.router)
app.include_router(players.router)
app.include_router(games.router)
app.include_router(standings.router)
app.include_router(rankings.router)
app.include_router(search.router)
app.include_router(ask.router)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Endpoint simples para verificar se a API está rodando."""
    return {
        "status": "ok",
        "project": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
    }


@app.get("/health/db", tags=["system"])
def database_health_check() -> dict[str, str]:
    """Endpoint simples para verificar se a conexão com SQLite está funcionando."""
    database_ok = check_database_connection()

    return {
        "status": "ok" if database_ok else "error",
        "database": "sqlite",
        "database_path": str(settings.database_path),
    }


@app.get("/health/schema", tags=["system"])
def schema_health_check() -> dict[str, object]:
    """Endpoint simples para verificar o catálogo de tabelas finais."""
    return {
        "status": "ok",
        "tables": len(FINAL_TABLE_SPECS),
        "table_names": [spec.table_name for spec in FINAL_TABLE_SPECS],
        "data_dir": str(settings.data_dir),
    }


@app.get("/health/data", tags=["system"])
def data_health_check() -> dict[str, object]:
    """Endpoint simples para verificar quantas linhas existem em cada tabela."""
    counts = get_table_counts(engine)

    missing_tables = [
        table_name
        for table_name, count in counts.items()
        if count < 0
    ]

    return {
        "status": "ok" if not missing_tables else "warning",
        "database_path": str(settings.database_path),
        "tables": counts,
        "missing_tables": missing_tables,
    }


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    """Endpoint raiz com uma mensagem básica."""
    return {
        "message": "DaTabela API",
        "docs": "/docs",
        "health": "/health",
        "database_health": "/health/db",
        "schema_health": "/health/schema",
        "data_health": "/health/data",
        "seasons": "/seasons",
        "teams": "/teams",
        "players": "/players",
        "games": "/games",
        "standings": "/standings",
        "player_rankings": "/rankings/players/metrics",
        "team_rankings": "/rankings/teams/metrics",
        "search": "/search?q=franca",
        "ask": "/ask",
        "ask_examples": "/ask/examples",
    }