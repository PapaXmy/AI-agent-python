# import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    open_api_key: str = ""
    open_base_url: str = ""
    chroma_db_path: str = "./chroma_db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


Path("./chroma_db").mkdir(exist_ok=True)


settings = Settings()
