import json
import logging
from pathlib import Path
from typing import List

import yaml
from langchain.schema import Document
from langchain_community.document_loaders import (Docx2txtLoader, PyPDFLoader,
                                                  TextLoader,
                                                  UnstructuredFileLoader)

logger = logging.getLogger(__name__)


def _load_metadata(meta_path: Path) -> dict:
    """Загружает метаданные из JSON или YAML файла"""
    if not meta_path.exists():
        logger.debug(f"Файл метаданных не найден: {meta_path}")
        return {}

    try:
        if meta_path.suffix == ".json":
            with open(meta_path, "r", encoding="utf-8") as f:
                logger.debug(f"Метаданные загружены из JSON: {meta_path}")
                return json.load(f)

        elif meta_path.suffix in [".yal", ".yaml"]:
            with open(meta_path, "r", encoding="utf-8") as f:
                logger.debug(f"Метаданные загружены из YAML: {meta_path}")
                return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки метаданных {meta_path}: {e}")
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
    logger.info(f"Начало загрузки документов из пути: {path}")

    for file in Path(path).rglob("*.*"):
        ext = file.suffix.lower()

        if ext not in loaders:
            logger.debug(f"Пропуск файла с неподдерживаемым расширением: {file}")
            continue

        try:
            logger.debug(f"Загрузка файла {file}")
            loader = loaders[ext](str(file))
            loaded_docs = loader.load()

            base_metadata = {
                "source": str(file),
                "file_name": file.name,
                "format": ext[1:],
            }

            custom_metadata = {}

            for meta_ext in [".meta.json", ".meta.yaml", "meta.yml"]:
                meta_path = file.with_suffix(file.suffix + meta_ext)

                if meta_path.exists():
                    custom_metadata = _load_metadata(meta_path)
                    logger.debug(
                        f"Загружены кастомные метаданные для {file}: {custom_metadata}"
                    )
                    break

            for doc in loaded_docs:
                doc.metadata.update(base_metadata)
                doc.metadata.update(custom_metadata)

            docs.extend(loaded_docs)
            logger.info(
                f"Успешно загружен файл: {file}, документов: {len(loaded_docs)}"
            )

        except Exception as e:
            logger.error(f"Ошибка загрузки {file}: {e}")

    logger.info(f"Всего загружено документов: {len(docs)}")
    return docs
