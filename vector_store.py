import logging
import os
import shutil

from langchain_community.vectorstores import Chroma

from config import settings
from embeddings import get_embeddings

logger = logging.getLogger(__name__)


def get_vector_store(
    documents=None,
    provider: str = "local",
    project_name: str = "default",
    model_name: str = "BAAI/bge-large-en",
):
    """Создает или загружает векторую базу данных"""
    logger.info(f"Инициализация векторной базы данных для коллекции: {project_name}")
    use_openai = provider == "local"
    embedding_function = get_embeddings(use_openai=use_openai, model_name=model_name)
    project_path = os.path.join(settings.chroma_db_path, project_name)
    os.makedirs(project_path, exist_ok=True)
    collection_name = f"{project_name}"

    if documents:
        logger.info(f"Создание новой векторной БД с {len(documents)} документами")
        vectordb = Chroma.from_documents(
            documents=documents,
            embedding=embedding_function,
            persist_directory=settings.chroma_db_path,
            collection_name=collection_name,
        )
        logger.info("Векторная БД успешно создана")
    else:
        logger.info("Загрузка существующей базы данных")
        vectordb = Chroma(
            persist_directory=settings.chroma_db_path,
            embedding_function=embedding_function,
            collection_name=collection_name,
        )
        logger.info("БД успешно загружена")

    return vectordb


def add_documents_to_store(
    docs, provider: str = "openai", project_name: str = "default"
):
    """Добавляет документы в существующее векторное хранилище"""
    logger.info(f"Добавление {len(docs)} документов в коллекцию: {project_name}")

    vectordb = get_vector_store(provider=provider, project_name=project_name)
    vectordb.add_documents(docs)
    vectordb.persist()

    logger.info("Документы успешно добавлены в БД")
    return vectordb


def list_project():
    """Возвращает список всех проектов базе данных"""
    logger.info("Получение списка проектов")
    projects = []

    if os.path.exists(settings.chroma_db_path):

        for item in os.listdir(settings.chroma_db_path):

            if os.path.isdir(os.path.join(settings.chroma_db_path, item)):
                projects.append(item)

    logger.info(f"Найдено проектов: {len(projects)}: {projects}")
    return projects


def delete_project(project_name: str):
    """Удаляет проект и все его данные"""
    logger.info(f"Попытка удаления коллекции: {project_name}")
    project_path = os.path.join(settings.chroma_db_path, project_name)

    if os.path.exists(project_path):
        shutil.rmtree(project_path)
        logger.info(f"Коллекция {project_name} успешно удалена")

        return True
    logger.warning(f"Коллекция {project_name} не найдена для удаления")
    return False
