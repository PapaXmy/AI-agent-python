import json
import logging
from typing import Dict, List

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from agents.base_agent import BaseAgent
from utils.config import settings

logger = logging.getLogger(__name__)


class PlannerAgent(BaseAgent):
    """Агент планировщик"""

    def __init__(self):
        super().__init__("planner", "default")

    def generate_plan(self, tech_spec: str) -> List[Dict]:
        """Генерирует план разработки на основе ТЗ"""
        prompt_template = """Ты - опытный менеджер проектов. Разбей следующее
        техническое задание на минимальное количество атомарных и 
        последовательных задач для разработчика Python. Ответ предоставь 
        ТОЛЬКО в виде валидного JSON-массива объектов. Каждый объект должен 
        иметь поля: "id" (порядковый номер), "description" (текстовое описание
        задачи) и "depends_on" (массив с id задач, от которых зависит эта задача).
        
        Техническое задание: {tech_spec}"""

        prompt = PromptTemplate(template=prompt_template, input_variables=["tech_spec"])

        llm = ChatOpenAI(
            model="gpt-4.1",
            temperature=0.1,
            api_key=settings.api_key,
            base_url=settings.base_url,
        )

        response = llm.invoke(prompt.format(tech_spec=tech_spec))

        try:
            plan = json.loads(response.content)
            logger.info(f"Сгенертрован план с {len(plan)} задачами")
            return plan
        except json.JSONDecodeError as e:
            logger.error(f"Очибка чтения файла JSON: {e}")
            return self._create_fallback_plan(tech_spec)

    def _create_fallback_plan(self, tech_spec: str) -> List[Dict]:
        """Создает простой план при ошибке"""
        return [
            {
                "id": 1,
                "description": f"Реализовать {tech_spec[:100]}...",
                "depends_on": [],
            }
        ]
