from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

from config import settings


def get_embeddings(use_openai: bool = True, model_name: str = "all-MiniLM-L6-v2"):
    """Возвращает объект эмбеддингов"""
    if use_openai:
        return OpenAIEmbeddings(
            open_api_key=settings.open_api_key, open_api_base=settings.open_base_url
        )
    else:
        return HuggingFaceEmbeddings(model_name=model_name)
