import json
import os
from pathlib import Path
from typing import List

from langchain.schema import Document
from langchain_community.document_loaders import (Doc2txtLoader, PyPDFLoader,
                                                  TextLoader)


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
