import os

from langchain.vectorstores import Chroma

from config import settings
from embeddings import get_embeddings


def get_vector_store(
    documents=None,
    provider: str = "openai",
    project_name: str = "default",
    model_name: str = "BAAI/bge-large-en",
):
    """Создает или загружает векторное хранилище"""
    use_openai = provider == "openai"
    embeddings_functions = get_embeddings(use_openai=use_openai, model_name=model_name)
    project_path = os.path.join(settings.chroma_db_path, project_name)
    os.makedirs(project_path, exist_ok=True)
    collection_name = f"{project_name}"

    if documents:
        vectordb = Chroma.from_documents(
            documents=documents,
            embedding=embeddings_functions,
            persist_directory=settings.chroma_db_path,
            collection_name=collection_name,
        )
    else:
        vectordb = Chroma(
            persist_directory=settings.chroma_db_path,
            embeddings_functions=embeddings_functions,
            collection_name=collection_name,
        )

    return vectordb


def add_documents_to_store(
    docs, provider: str = "openai", project_name: str = "default"
):
    """Добавляет документы в существующее векторное хранилище"""
    vectordb = get_vector_store(provider=provider, project_name=project_name)
    vectordb.add_documents(docs)
    vectordb.persist()
    return vectordb


def list_project():
    """Возвращает список всех проектов базе данных"""
    projects = []
    if os.path.exists(settings.chroma_db_path):
        for item in os.listdir(settings.chroma_db_path):
            if os.path.isdir(os.path.join(settings.chroma_db_path, item)):
                projects.append(item)
    return projects


def delete_project(project_name: str):
    """Удаляет проект и все его данные"""
    project_path = os.path.join(settings.chroma_db_path, project_name)
    if os.path.exists(project_path):
        import shutil

        shutil.rmtree(project_path)
        return True
    return False
