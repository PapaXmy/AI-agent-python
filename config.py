from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_api_base: str = ""
    chroma_db_path: str = "./chroma_db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


Path("./chroma_db").mkdir(exist_ok=True)


settings = Settings()
