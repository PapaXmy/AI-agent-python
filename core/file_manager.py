import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FileManager:
    """Утилиты для работы с файлами"""

    @staticmethod
    def read_file_content(file_path: Path) -> str:
        """Читает содержимое файла"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Ошибка чтения файла {file_path}: {e}")
            return ""

    @staticmethod
    def write_file_content(file_path: Path, content: str):
        """Запись в файл"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Файл записан: {file_path}")
        except Exception as e:
            logger.error(f"Ошибка записи файла {file_path}: {e}")

    @staticmethod
    def get_project_structure(project_path: Path) -> str:
        """Возвращает структуру файлов проекта в виде строки"""
        structure = []
        for file in project_path.rglob("*"):
            if file.is_file():
                structure.append(str(file.relative_to(project_path)))
        return "\n".join(structure)
