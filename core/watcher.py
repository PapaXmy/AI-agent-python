from pathlib import Path
from watchdog.events import FileSystemEventHandler
from utils.rag_manager import RAGManager
import logging

logger = logging.getLogger(__name__)

WATCHED_EXTENSIONS = {".py", ".md", ".txt"}


class ProjectChangeHandler(FileSystemEventHandler):
    """Отслеживание изменений в проекте"""

    def __init__(self, project_name: str, project_path: str):
        self.rag_manager = RAGManager(project_name)
        self.project_path = project_path

    def on_modified(self, event):
        """Отслеживает изменения файлов"""
        path = Path(event.src_path)
        if not event.is_directory and path.suffix in WATCHED_EXTENSIONS:
            logger.info(f"Файл изменен {path}")
            self.rag_manager.update_file(path)

