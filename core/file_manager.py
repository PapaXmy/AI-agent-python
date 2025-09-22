import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FileManager:
    @staticmethod
    def read_file_content(file_path: Path) -> str:
        """Читает содержимое файла"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Ошибка чтения файла {file_path}: {e}")
            return ""
