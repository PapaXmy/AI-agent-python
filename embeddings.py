# import os

from langchain.embeddings import SentenceTransformerEmbeddings
# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai.embeddings import OpenAIEmbeddings

from config import settings


class BgeEmbeddings(SentenceTransformerEmbeddings):
    """Обертка для bge-моделей, чтобы запросы шли с инструкцией"""

    def embed_query(self, text: str):
        instruction = "Represent this sentence for searching relevant passeges:"
        return super().embed_query(instruction + text)


def get_embeddings(use_openai: bool = True, model_name: str = "BAAI/bge-large-en"):
    """Инициализация эмбеддингов для Chroma"""
    if use_openai:
        if not settings.openai_api_key:
            raise ValueError("Нет ключа OpenAI API, проверте файл .env")

        openai_kwargs = {
            "model": "text-embedding-3-large",
            "openai_api_key": settings.openai_api_key,
        }

        if settings.openai_base_url:
            openai_kwargs["openai_base_url"] = settings.openai_base_url

        embeddings = OpenAIEmbeddings(**openai_kwargs)
    else:
        if "bge" in model_name.lower():
            embeddings = BgeEmbeddings(model_name=model_name)
        else:
            embeddings = SentenceTransformerEmbeddings(model_name=model_name)

    return embeddings
