import logging
import os
from pathlib import Path
from typing import Any, Dict, List

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from loaders_mmanager import LoadersManager

from .config import settings
from .embeddings import get_embeddings

logger = logging.getLogger(__name__)


class RAGManager:
    """Централизованный менеджер для работы с RAG системой"""

    def __init__(self, project_name: str = "default"):
        self.project_name = project_name
        self.vector_db = None
        self.initialized = False
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        self.load_documents = LoadersManager()
        self._initialize_vector_store()

    def _initialize_vector_store(
        self,
        provider: str = "local",
        model_name: str = "BAAI/bge-large-en",
    ):
        """Создает или загружает векторую базу данных"""
        logger.info(
            f"Инициализация векторной базы данных для коллекции: {self.project_name}"
        )
        try:
            use_openai = provider == "local"
            embedding_function = get_embeddings(
                use_openai=use_openai, model_name=model_name
            )
            project_path = Path(settings.chroma_db_path) / self.project_name
            project_path.mkdir(parents=True, exist_ok=True)

            self.vector_db = Chroma(
                embedding_function=embedding_function,
                persist_directory=str(project_path),
                collection_name=self.project_name,
            )

            data = self.vector_db.get()
            if data and data.get("ids") > 0:
                self.initialized = True
                logger.info(f"Векторная база для {self.project_name} загружена")
            else:
                logger.warning(f"Коллекция {self.project_name} пустая")

        except Exception as e:
            logger.error(f"Ошибка инициализации векторной базы данных")
