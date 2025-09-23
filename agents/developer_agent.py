import logging
import re
from pathlib import Path

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

    def execute_task(self, task: dict, project_state):
        """ВЫполняет задачу разработки"""
        project_context = self.get_project_context(project_state.session_path)

        prompt_template = """Ты - senior Python-разработчик. Выполни задачу. У
        тебя есть доступ к текущим файлам проекта.
        
        ЗАДАЧА: {task_description}
        
        ТЕКУЩИЕ ФАЙЛЫ ПРОЕКТА:
        {project_context}
        
        В своем ответе ты должен указать ТОЛЬКО код, который нужно изменить, в формате:
        START_FILENAME: {путь_к_файлу}
        {код файла целиком}
        END_FILENAME: {путь_к_файлу}
        
        Если файл новый, создай его. Если изменяешь существующий, предоставь
        ПОЛНЫЙ код файла с изменениями."""

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["task_description", "project_context"],
        )

        llm = ChatOpenAI(
            model="gpt-4.1",
            temperature=0.1,
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.openai_api_base,
        )

        response = llm.invoke(
            prompt.format(
                task_description=task["description"], project_context=project_context
            )
        )

        self.apply_changes(response.content, project_state.session_path)

    def get_project_context(self, project_path: Path):
        """Возвращает контекст проекта (все файлы и их содержимое)"""
        context = []
        for file in project_path.rglob("*"):
            if file.is_file():
                content = FileManager.read_file_content(file)
                context.append(f"{file.relative_to(project_path)}:\n{context}\n")

        return "\n".join(context)

    def apply_changes(self, response: str, project_path: Path):
        """Применяет изменения к файлам проекта на основе ответа LLM"""
        pattern = r"START_FILENAME:\s*(.+?)\n(.*?)END_FILENAME:\s*\1"
        matches = re.findall(pattern, response, re.DOTALL)

        for (
            file_path,
            content,
        ) in matches:
            full_path = project_path / file_path.strip()
            FileManager.write_file_content(full_path, content.strip())
            logger.info(f"Файл обновлен: {file_path}")
