from langchain.vectorstores import Chroma

from config import settings
from embeddings import get_embeddings


def get_vector_store(documents=None, provider: str = "openai"):
    """Создает или загружает векторное хранилище"""
    use_openai = provider == "openai"
    embeddings = get_embeddings(use_openai=use_openai)

    if documents:
        vectordb = Chroma.from_documents(
            documents=documents,
            embeddings=embeddings,
            persist_directory=settings.chroma_db_path,
        )
    else:
        vectordb = Chroma(
            persist_directory=settings.chroma_db_path, embeddings_functions=embeddings
        )

    return vectordb


def add_documents(docs, provider: str = "openai"):
    """Добавляет документы в существующее векторное хранилище"""
    vectordb = get_vector_store(provider)
    vectordb.add_documents(docs)
    vectordb.persist()
