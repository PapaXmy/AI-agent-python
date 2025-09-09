from langchain.vectorstores import Chroma

import embeddings
from config import settings
from embeddings import get_embeddings


def get_vector_store(provider: str = "openai"):
    embeddings = get_embeddings(provider)
    vectordb = Chroma(
        collection_name="documents",
        embeddings_function=embeddings,
        persist_directory=settings.chroma_db_path,
    )
    return vectordb


def add_documents(docs, provider: str = "openai"):
    vectordb = get_vector_store(provider)
    vectordb.add_documents(docs)
    vectordb.persist()
