import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging():
    """Настройка логирования агента"""

    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    formatter = logging.Formatter(
        "%(asctime)s - %(name) - %(levelname)s - %(messages)s"
    )

    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "ai_agent.log"), maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    logging.getLogger("Langchain").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("https").setLevel(logging.WARNING)
