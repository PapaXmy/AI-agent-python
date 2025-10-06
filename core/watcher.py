from pathlib import Path
import time
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
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
        """Записывает изменения файлов в БД"""
        path = Path(event.src_path)
        if not event.is_directory and path.suffix in WATCHED_EXTENSIONS:
            logger.info(f"Файл изменен {path}")
            self.rag_manager.update_file(path)

    def on_created(self, event):
        """Записывает созданые файлы в БД"""
        path = Path(event.src_path)
        if not event.is_directory and path.suffix in WATCHED_EXTENSIONS:
            logger.info(f"Файл создан: {path}")
            self.rag_manager.update_file(path)

    def on_delete(self, event):
        """Удаляет файлы из БД"""
        path = Path(event.src_path)
        if not event.is_directory and path.suffix in WATCHED_EXTENSIONS:
            logger.info(f"Файл удален {path}")
            self.rag_manager.remove_file(path)

def start_project_watcher(project_name: str, project_path: Path):
    """Запускает слежение за проектом"""
    event_handler = ProjectChangeHandler(project_name, project_path)
    observer = Observer()
    observer.schedule(event_handler, str(project_path), recursive=True)
    observer.start()
    logger.info(f"Слежение запущено за: {project_path}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("Слежение остановлено в ручную")
    observer.join()
