import json
from pathlib import Path
from typing import List

import yaml
from langchain.schema import Document
from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredFileLoader,
)


def _load_metadata(meta_path: Path) -> dict:
    """Загружает метаданные из JSON или YAML файла"""
    if not meta_path.exists():
        return {}

    try:
        if meta_path.suffix == ".json":
            with open(meta_path, "r", encoding="utf-8") as f:
                return json.load(f)

        elif meta_path.suffix in [".yal", ".yaml"]:
            with open(meta_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
    except Exception as e:
        print(f"Ошибка загрузки метаданных {meta_path}: {e}")
    return {}


def load_documents(path: str):
    """Загружает документы и подгружает кастомные метаданные из .meta.json/ .meta.yaml"""
    loaders = {
        ".txt": TextLoader,
        ".md": TextLoader,
        ".py": TextLoader,
        ".pdf": PyPDFLoader,
        ".docx": Docx2txtLoader,
        ".doc": Docx2txtLoader,
        ".html": UnstructuredFileLoader,
    }

    docs: List[Document] = []
    for file in Path(path).rglob("*.*"):
        ext = file.suffix.lower()
        if ext not in loaders:
            continue

        try:
            loader = loaders[ext](str(file))
            loaded_docs = loader.load()

            base_metadata = {
                "source": str(file),
                "file_name": file.name,
                "format": ext[1:],
            }

            meta_json = file.with_suffix(file.suffix + ".meta.json")
            meta_yaml = file.with_suffix(file.suffix + ".meta.yaml")

            custom_matadata = {}
            if meta_json.exists():
                custom_metadata = _load_metadata(meta_json)
            elif meta_yaml.exists():
                custom_matadata = _load_metadata(meta_yaml)

            for d in loaded_docs:
                d.matadata.update(base_metadata)
                d.metadata.update(custom_matadata)

            docs.extend(loaded_docs)

        except Exception as e:
            print(f"Ошибка загрузки {file}: {e}")

    return docs
