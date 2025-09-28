import logging
import uuid
from pathlib import Path
from typing import Any, Dict

from agents.developer_agent import DeveloperAgent
from agents.planer_agent import PlannerAgent
from core.file_manager import FileManager

from .project_state import ProjectState

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(self):
        self.active_session: Dict[str, ProjectState] = {}
        self.planner = PlannerAgent()
        self.developer = DeveloperAgent()
        logger.info("Оркестратор инициализирован")

    def start_new_session(self, tech_spec: str) -> str:
        """Создает новую сессию и возвращает ее ID"""
        session_id = str(uuid.uuid4())
        session_path = Path(f"./projects/{session_id}")
        session_path.mkdir(parents=True, exist_ok=True)

        # состояние проекта
        project_state = ProjectState(session_id, session_path)
        self.active_session[session_id] = project_state

        # сохранение ТЗ в текстовый файл
        FileManager.write_file_content(session_path / "tech_spec.txt", tech_spec)
        project_state.update_status("planning")

        try:
            # запуск планировщика

            plan = self.planner.generate_plan(tech_spec)
            project_state.update_plan(plan)
            project_state.update_status("coding")

            for task in plan:
                logger.info(f"Обработка задачи {task['id']}")
                result = self.developer.execute_task(task, project_state)
                project_state.update_status(f"coding_task_{task['id']}")

            project_state.update_status("completed")
            logger.info(f"Сессия {session_id} завершена")

        except Exception as e:
            project_state.update_status(f"error: {str(e)}")
            logger.exception("")
            logger.error(f"Ошибка сессии {session_id}: {e}")

        return session_id

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
