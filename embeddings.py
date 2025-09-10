# import os

from langchain.embeddings import SentenceTransformerEmbeddings

# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai.embeddings import OpenAIEmbeddings

from config import settings


def get_embeddings(use_openai: bool = True, model_name: str = "all-MiniLM-L6-v2"):
    """Инициализация эмбеддингов для Chroma"""
    if use_openai:
        if not settings.openai_api_key:
            raise ValueError("Нет ключа OpenAI API, проверте файл .env")

        openai_kwargs = {
            "model": "text-embeddings-ada-002",
            "openai_api_key": settings.openai_api_key,
        }

        if settings.openai_base_url:
            openai_kwargs["openai_base_url"] = settings.openai_base_url

        embeddings = OpenAIEmbeddings(**openai_kwargs)
    else:
        embeddings = SentenceTransformerEmbeddings(model_name=model_name)

    return embeddings
