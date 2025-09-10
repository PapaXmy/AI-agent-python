import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    open_api_key: str = os.getenv("OPEN_API_KEY", "")
    open_base_url: str = os.getenv("OPEN_BASE_URL", "")
    croma_db_path: str = os.getenv("CHROMA_DB_PATH", "")

    class Config:
        env_file = ".env"


settings = Settings()
