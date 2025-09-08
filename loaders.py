from pathlib import Path

from langchain_community.document_loaders import TextLoader


def load_documents(path: str):
    docs = []
    for file in Path(path).rglob("*.*"):
        if file.suffix in [".txt", ".md", ".py"]:
            loader = TextLoader(str(file))
            docs.extend(loader.load())
    return docs
