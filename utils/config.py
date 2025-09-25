import logging
from pathlib import Path

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_api_base: str = ""
    chroma_db_path: str = "./chroma_db"

    embeddings_provider: str = "local"
    embeddings_model: str = "BAAI/bge-large-en"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


try:
    Path("./chroma_db").mkdir(exist_ok=True)
    Path("./logs").mkdir(exist_ok=True)
    Path("./projects").mkdir(exist_ok=True)
    Path("./docs").mkdir(exist_ok=True)
    logger.info("Директория для Chroms DB создана или уже существует")
except Exception as e:
    logger.error(f"Ошибка создания директории для Chroma DB: {e}")


settings = Settings()
logger.info("Настройки приложения загружены")
