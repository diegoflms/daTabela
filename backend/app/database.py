from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

settings.database_dir.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base declarativa dos models SQLAlchemy."""


def get_db() -> Generator[Session, None, None]:
    """Dependência do FastAPI para abrir e fechar sessão do banco."""
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> bool:
    """Verifica se a API consegue abrir conexão com o SQLite."""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1")).scalar_one()

    return result == 1