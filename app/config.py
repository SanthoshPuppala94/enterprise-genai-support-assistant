from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "lws_mock.db"
DOCS_DIR = DATA_DIR / "docs"
LOGS_DIR = DATA_DIR / "logs"

load_dotenv(ROOT_DIR / ".env")


class Settings(BaseSettings):
    app_name: str = "Enterprise LWS GenAI Assistant"
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    openai_model: str = "gpt-4o-mini"
    vector_store_backend: str = "chroma"
    db_path: Path = DB_PATH

    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

