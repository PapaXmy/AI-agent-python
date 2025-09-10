import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    openai_base_url: str | None = None
    chroma_db_path: str = "./chroma_db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
