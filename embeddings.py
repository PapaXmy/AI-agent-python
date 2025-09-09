from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

from config import settings


def get_embeddings(provider: str = "openai"):
    if provider == "openai":
        return OpenAIEmbeddings(
            open_api_key=settings.open_api_key, open_api_base=settings.open_base_url
        )
    elif provider == "huggingface":
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    else:
        raise ValueError("Unknow embeddings provider")
