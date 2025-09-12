# import os

from typing import List

# from langchain.embeddings import SentenceTransformerEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai.embeddings import OpenAIEmbeddings

from config import settings


class BgeEmbeddings(HuggingFaceEmbeddings):
    """Обертка для bge-моделей, чтобы запросы шли с инструкцией"""

    def embed_query(self, text: str):
        instruction = "Represent this sentence for searching relevant passeges:"
        return super().embed_query(f"{instruction} {text}")

    def embed_documents(self, texts: List[str]):
        return super().embed_documents(texts)


def get_embeddings(use_openai: bool = False, model_name: str = "BAAI/bge-large-en"):
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
            embeddings = BgeEmbeddings(
                model_name=model_name,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
        else:
            embeddings = HuggingFaceEmbeddings(model_name=model_name)

    return embeddings
