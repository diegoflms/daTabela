from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PROJECT_ROOT.parent


class Settings(BaseSettings):
    """Configurações globais da API."""

    app_name: str = "DaTabela API"
    app_version: str = "0.1.0"
    app_env: str = "development"

    database_dir: Path = PROJECT_ROOT / "database"
    database_name: str = "databela.sqlite3"

    data_dir: Path = REPOSITORY_ROOT / "data" / "dados"
    runtime_data_dir: Path = REPOSITORY_ROOT / "data" / "dados" / "_runtime"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_path(self) -> Path:
        return self.database_dir / self.database_name

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.database_path.as_posix()}"


@lru_cache
def get_settings() -> Settings:
    """Retorna as configurações cacheadas da aplicação."""
    return Settings()