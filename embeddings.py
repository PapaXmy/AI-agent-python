import os

from langchain.embeddings import SentenceTransformerEmbeddings

# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai.embeddings import OpenAIEmbeddings

from config import settings


def get_embeddings(provider: str = "openai", model_name: str = "all-MiniLM-L6-v2"):
    """Инициализация эмбеддингов для Chroma"""
    if provider == "openai":
        os.environ["OPEN_API_KEY"] = settings.open_api_key
        if settings.open_base_url:
            os.environ["OPEN_API_BASE"] = settings.open_base_url

        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    else:
        embeddings = SentenceTransformerEmbeddings(model_name=model_name)
    return embeddings
