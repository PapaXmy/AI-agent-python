import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    open_api_key: str = os.getenv("open_api_key", "")
    open_base_url: str = os.getenv("open_base_url", "")
    chroma_db_path: str = os.getenv("chroma_db_path", "")

    class Config:
        env_file = ".env"


settings = Settings()
