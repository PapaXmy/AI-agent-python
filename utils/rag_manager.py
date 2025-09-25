import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from loaders_mmanager import LoadersManager

from .config import settings
from .embeddings import get_embeddings

logger = logging.getLogger(__name__)


class RAGManager:
    """Централизованный менеджер для работы с RAG системой"""

    def __init__(
        self,
        project_name: str = "default",
        provider: str = "local",
        model_name: str = "BAAI/bge-large-en",
    ):
        self.project_name = project_name
        self.provider = provider
        self.model_name = model_name
        self.vector_db = None
        self.initialized = False
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        self.load = LoadersManager()
        self._initialize_vector_store()

    def _initialize_vector_store(self, documents: Optional[List[Document]] = None):
        """Создает или загружает векторую базу данных"""
        logger.info(
            f"Инициализация векторной базы данных для коллекции: {self.project_name}"
        )
        try:
            use_openai = self.provider == "local"
            embedding_function = get_embeddings(
                use_openai=use_openai, model_name=self.model_name
            )
            project_path = os.path.join(settings.chroma_db_path, self.project_name)
            os.makedirs(project_path, exist_ok=True)
            collection_name = f"{self.project_name}"

            if documents:
                logger.info(
                    f"Создание новой векторной БД с {len(documents)} документами"
                )
                self.vector_db = Chroma.from_documents(
                    documents=documents,
                    embedding_function=embedding_function,
                    persist_directory=project_path,
                    collection_name=collection_name,
                )
                self.initialized = True
                logger.info("Векторная БД успешно создана")
            else:
                logger.info(f"Загрузка существующей базы данных {self.project_name}")
                self.vector_db = Chroma(
                    persist_directory=project_path,
                    embedding_function=embedding_function,
                    collection_name=collection_name,
                )
                self.initialized = True

                # data = self.vector_db.get()
                # if data and data.get("ids") > 0:
                #     self.initialized = True
                #     logger.info(f"Векторная база для {self.project_name} загружена")
                # else:
                #     logger.warning(f"Коллекция {self.project_name} пустая")
                #
        except Exception as e:
            logger.error(f"Ошибка инициализации векторной базы данных {e}")
            self.initialized = False

    def initianilize_knoledge_base(self, docs_path: str) -> bool:
        """Инициализирует базу знаний с документацией из указанного пути"""
        logger.info(f"Инициализация БД из {docs_path}")
        try:
            raw_documents = self.load.load_documents(docs_path)
            if not raw_documents:
                logger.error("Не найдено документов для загрузки")
                return False

            documents = self.text_splitter.split_documents(raw_documents)
            logger.info(f"Документы разбиты на {len(documents)} чанков")

            self._initialize_vector_store(documents)

            if self.initialized:
                logger.info(f"База знаний инициализирована с {len(documents)} чанками")
                return True
            else:
                logger.error("База знаний не инициализирована")
                return False
        except Exception as e:
            logger.error(f"Ошибка инициализации базы знаний {e}")
            return False

    def add_document(self, docs_path: str) -> bool:
        """Добавляет новые документы в базу данных"""
        try:
            if not self.vector_db or not self.initialized:
                logger.error("База данных не инициализирована")
                return False

            raw_documents = self.load.load_documents(docs_path)
            if not raw_documents:
                logger.error("Ненайдено документов для добавления")
                return False
            documents = self.text_splitter.split_documents(raw_documents)
            self.vector_db.add_documents(documents)

            logger.info(f"Добавлено {len(documents)} документов в базу знаний")
            return True

        except Exception as e:
            logger.error(f"Ошибка добавления документов: {e}")
            return False
