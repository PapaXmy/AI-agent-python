import logging
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from agents.developer_agent import DeveloperAgent
from agents.planer_agent import PlannerAgent
from core.file_manager import FileManager

from .project_state import ProjectState

logger = logging.getLogger(__name__)


class Orchestrator:
    """Оркестратор для агентов"""

    def __init__(self):
        self.active_session: Dict[str, ProjectState] = {}
        self.planner = PlannerAgent()
        self.developer = DeveloperAgent()
        logger.info("Оркестратор инициализирован")

    def start_new_session(self, tech_spec: str, session_id: str) -> str:
        """Создает новую или продорлжает существующую сессию"""
        if session_id is not None and session_id in self.active_session:
            return self.continue_session(session_id, tech_spec)
        else:
            return self._create_new_session(tech_spec, session_id)

    def _create_new_session(self, tech_spec: str, session_id: str) -> str:
        """Создает новую cессию"""
        # session_id = str(uuid.uuid4())
        session_path = Path(f"./projects/{session_id}")
        session_path.mkdir(parents=True, exist_ok=True)

        # состояние проекта
        project_state = ProjectState(session_id, session_path)
        self.active_session[session_id] = project_state

        project_state.start_iteration(tech_spec)

        try:
            # запуск планировщика

            plan = self.planner.generate_plan(tech_spec)
            project_state.update_plan(plan)

            self._execute_plan(plan, project_state)

            project_state.complete_iteration()
            logger.info(f"Сессия {session_id} завершена")

        except Exception as e:
            project_state.status = f"Ошибка: {str(e)}"
            logger.error(f"Ошибка в сессии {session_id}: {e}")
            logger.exception("")

        return session_id

    def continue_session(self):
        """Продолжает существующую сессию с нвой итерацией"""
        pass

    def _execute_plan(self):
        """Выполняет план задач"""
        pass

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Возвращает статус сессии"""
        if session_id not in self.active_session:
            return {"error": "Сессия не найдена"}

        return self.active_session[session_id].get_status()
