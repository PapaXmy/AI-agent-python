import logging
from typing import List

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai.embeddings import OpenAIEmbeddings

from .config import settings

logger = logging.getLogger(__name__)


class BgeEmbeddings(HuggingFaceEmbeddings):
    """Обертка для bge-моделей, чтобы запросы шли с инструкцией"""

    def embed_query(self, text: str):
        logger.debug(f"Встраивание запроса: {text[:50]}...")
        instruction = "Represent this sentence for searching relevant passeges:"
        return super().embed_query(f"{instruction} {text}")

    def embed_documents(self, texts: List[str]):
        logger.debug(f"Встраиване {len(texts)} документов")
        return super().embed_documents(texts)


def get_embeddings(use_openai: bool = False, model_name: str = "BAAI/bge-large-en"):
    """Инициализация эмбеддингов для Chroma"""
    logger.info(
        f"Инициализация эмбеддингов, use_openai={use_openai}, modrl={model_name}"
    )

    if use_openai:

        if not settings.api_key:
            error_msg = "Нет ключа OpenAI API, проверте файл .env"
            logger.error(error_msg)
            raise ValueError(error_msg)

        openai_kwargs = {
            "model": "text-embedding-3-large",
            "openai_api_key": settings.api_key,
        }

        if settings.base_url:
            openai_kwargs["openai_api_base"] = settings.base_url
            logger.debug("Использование кастомного OpenAI API URL")

        embeddings = OpenAIEmbeddings(**openai_kwargs)
        logger.info("OpenAI эмбеддинги инициализированы")
    else:

        if "bge" in model_name.lower():
            logger.info(f"Использованеи BGE эмбеддингов: {model_name}")
            embeddings = BgeEmbeddings(
                model_name=model_name,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
        else:
            logger.info(f"Использованеи HuggingFace эмбеддингов: {model_name}")
            embeddings = HuggingFaceEmbeddings(model_name=model_name)

    logger.info("Эмбеддинги успешно инициализированы")
    return embeddings
