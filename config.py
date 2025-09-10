# import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
<<<<<<< HEAD
    openai_api_key: str
    openai_base_url: str | None = None
=======
    open_api_key: str = ""
    open_base_url: str = ""
>>>>>>> config/fix
    chroma_db_path: str = "./chroma_db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
<<<<<<< HEAD
=======
        extra = "allow"


Path("./chroma_db").mkdir(exist_ok=True)
>>>>>>> config/fix


settings = Settings()
