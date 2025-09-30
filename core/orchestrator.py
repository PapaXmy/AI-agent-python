import logging
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

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

    def start_new_session(
        self, tech_spec: str, session_id: Optional[str] = None
    ) -> str:
        """Создает новую или продорлжает существующую сессию"""
        if session_id is not None and session_id in self.active_session:
            return self.continue_session(session_id, tech_spec)
        else:
            return self._create_new_session(tech_spec)

    def _create_new_session(self, tech_spec: str) -> str:
        """Создает новую cессию"""
        session_id = str(uuid.uuid4())
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

    def continue_session(self, session_id: str, tech_spec: str) -> str:
        """Продолжает существующую сессию с нвой итерацией"""
        if session_id not in self.active_session:
            raise ValueError(f"Сессия {session_id} не найдена")

        project_state = self.active_session[session_id]
        project_state.start_iteration(tech_spec)

        try:
            plan = self.planner.generate_plan(tech_spec)
            project_state.update_plan(plan)

            self._execute_plan(plan, project_state)

            project_state.complete_iteration()
            logger.info(
                f"Сессия {session_id} обновлена, итерация {project_state.iteration}"
            )

        except Exception as e:
            project_state.status = f"error_iteration_{project_state.iteration}"
            logger.error(
                f"Ошибка итерации {project_state.iteration} сессии {session_id}: {e}"
            )
            logger.exception("")

        return session_id

    def _execute_plan(self, plan: List[Dict], project_state: ProjectState):
        """Выполняет план задач"""
        for task in plan:
            logger.info(f"Обработка задачи {task['id']}")
            result = self.developer.execute_task(task, project_state)
            project_state.status = (
                f"coding_task_{task['id']}_iteration_{project_state.iteration}"
            )

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Возвращает статус сессии"""
        if session_id not in self.active_session:
            return {"error": "Сессия не найдена"}

        return self.active_session[session_id].get_status()

    def get_active_session(self, project_state: ProjectState) -> List[Dict[str, Any]]:
        """Возвращает список активных сессий"""
        sessions = []
        for session_id in self.active_session.items():
            sessions.append(
                {
                    "session_id": session_id,
                    "status": project_state.status,
                    "iteration": project_state.iteration,
                    "created_at": project_state.created_at.isoformat(),
                    "updated_at": project_state.updated_at.isoformat(),
                }
            )
        return sessions

    def close_session(self, session_id: str) -> bool:
        """Закрывает сессию"""
        if session_id in self.active_session:
            self.active_session[session_id].status = "closed"
            return True
        return False

    def list_projects(self) -> List[Dict[str, Any]]:
        """Возвращает список всех проектов"""
        projects = []

        for project_name, project in self.active_session.items():
            projects.append(
                {
                    "project_name": project_name,
                    "status": project.status,
                    "iteration": project.iteration,
                    "created_at": project.created_at.isoformat(),
                    "updated_at": project.updated_at.isoformat(),
                }
            )

        return projects
