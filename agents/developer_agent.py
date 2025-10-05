import logging
import re
from pathlib import Path
from typing import Dict

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from agents.base_agent import BaseAgent
from core.file_manager import FileManager
from utils.config import settings

logger = logging.getLogger(__name__)


class DeveloperAgent(BaseAgent):
    """Агент разработчик"""

    def __init__(self):
        super().__init__("developer", "default")

    def execute_task(self, task: Dict, project_state) -> Dict:
        """ВЫполняет задачу разработки"""
        logger.info(f"Выполнение задачи: {task['id']} - {task['description']}")

        project_context = project_state.get_current_files_context()
        rag_context = self.get_rag_context(f"Разработка {task['description']}")

        prompt_template = """
        Ты - senior Python-разработчик. Выполни задачу.

        ВАЖНО: В путях к файлам используйте только прямые слеши (/), не используйте обратные слеши (\).
        Убедитесь, что путь заканчивается на правильное расширение файла (.py, .txt и т.д.)

        КОНТЕКСТ ДОКУМЕНТАЦИИ:
        {rag_context}

        ЗАДАЧА: {task_description}

        ТЕКУЩИЕ ФАЙЛЫ ПРОЕКТА:
        {project_context}
        
        Важно: Это итеративная разработка. Файлы уже существуют.
        - если файл существует, модифицируй его содержимое
        - если файл новый, создай его
        - сохраняй работоспособность существующего кода

        В своем ответе ты должен указать ТОЛЬКО код, который нужно изменить, в формате:
        START_FILENAME: путь/к/файлу.py
        код файла целиком
        END_FILENAME: путь/к/файлу.py
        
        Если файл новый, создай его. Если изменяешь существующий, предоставь
        ПОЛНЫЙ код файла с изменениями."""

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["task_description", "project_context", "rag_context"],
        )

        llm = ChatOpenAI(
            model="gpt-4.1",
            temperature=0.1,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )

        response = llm.invoke(
            prompt.format(
                task_description=task["description"],
                project_context=project_context,
                rag_context=rag_context,
            )
        )

        changes = self._apply_changes(project_state.project_path, response.content)

        return {
            "status": "completed",
            "task_id": task["id"],
            "changes": changes,
            "message": f"Задача: {task['id']} выполнена",
        }

    def _get_project_context(self, project_path: Path) -> str:
        """Возвращает контекст проекта"""
        context = []

        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix in [".py", ".txt", ".md", ".json"]:
                content = FileManager.read_file_content(file)
                context.append(f"{file.relative_to(project_path)}: \n{content}\n")

        return "\n".join(context) if context else "Фалы контекста отсутствуют"

    def _apply_changes(
        self, project_path: Path, parsed_files: dict[str, str]
    ) -> dict[str, str]:
        """Применяет изменения к файлам проекта на основе ответа LLM"""
        # pattern = r"START_FILENAME:\s*(.+?)\n(.*?)END_FILENAME:\s*\1"
        # matches = re.findall(pattern, response, re.DOTALL)

        changes = {}
        for (
            file_path,
            content,
        ) in parsed_files.items():
            # file_path = self._normalize_file_path(file_path.strip())

            if not file_path or not file_path.strip():
                logger.warning("Пропущен пустой путь к файлу")
                continue

            full_path = project_path / file_path
            created = not full_path.exists()

            full_path.parent.mkdir(parents=True, exist_ok=True)

            # if full_path.exists() and full_path.is_dir():
            #     logger.warning(f"Путь {full_path} является директорией")
            #     continue

            try:
                FileManager.write_file_content(full_path, content.strip())
                changes[file_path] = "создан" if created else "изменен"
                logger.info(
                    f"Файл обновлен: {file_path} {'создан' if created else 'обновлен'}"
                )
            except Exception as e:
                logger.error(f"Ошибка применения изменений к файлу {file_path}: {e}")
                logger.exception("")

        return changes

    def _normalize_file_path(self, file_path: str) -> str:
        """Нормализует путь к файлу"""
        normalized = file_path.replace("\\", "/")
        normalized = re.sub(r"/+", "/", normalized)
        normalized = normalized.strip("/")
        normalized = re.sub(r"^\.+/", "", normalized)
        return normalized
