import os

from langchain.vectorstores import Chroma

from config import settings
from embeddings import get_embeddings


def get_vector_store(
    documents=None, provider: str = "openai", project_name: str = "default"
):
    """Создает или загружает векторное хранилище"""
    use_openai = provider == "openai"
    embeddings = get_embeddings(use_openai=use_openai)
    project_path = os.path.join(settings.chroma_db_path, project_name)
    os.makedirs(project_path, exist_ok=True)
    collection_name = f"{project_name}"

    if documents:
        vectordb = Chroma.from_documents(
            documents=documents,
            embeddings=embeddings,
            persist_directory=settings.chroma_db_path,
            collection_name=collection_name,
        )
    else:
        vectordb = Chroma(
            persist_directory=settings.chroma_db_path,
            embeddings_functions=embeddings,
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
