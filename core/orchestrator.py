import logging
import uuid
from pathlib import Path
from typing import Any, Dict

from agents.developer_agent import DeveloperAgent
from agents.planer_agent import PlannerAgent

from .project_state import ProjectState

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(self):
        self.active_session: Dict[str, ProjectState] = {}

        def start_new_session(self, tech_spec: str) -> str:
            """Создает новую сессию и возвращает ее ID"""
            session_id = str(uuid.uuid4())
            session_path = Path(f"./projects/{session_id}")
            session_path.mkdir(parents=True, exist_ok=True)

            # состояние проекта
            project_state = ProjectState(session_id, session_path)
            self.active_session[session_id] = project_state

            # сохранение ТЗ в текстовый файл
            with open(session_path / "tech_spec.txt", "w") as f:
                f.write(tech_spec)

            # запуск планировщика
            planner = PlannerAgent()
            plan = planner.generate_plan(tech_spec)

            # раздаем задачи для разработчика
            developer = DeveloperAgent()
            for task in plan:
                developer.execute_task(task, project_state)

            return session_id

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Возвращает статус сессии"""
        if session_id not in self.active_session:
            return {"error": "Сессия не найдена"}

        return self.active_session[session_id].get_status()
