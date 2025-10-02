import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from agents.developer_agent import DeveloperAgent
from agents.planer_agent import PlannerAgent

from .project_state import ProjectState

logger = logging.getLogger(__name__)


class Orchestrator:
    """Оркестратор для агентов"""

    def __init__(self, projects_root: str = "./projects"):
        self.projects_root = Path(projects_root)
        self.projects_root.mkdir(parents=True, exist_ok=True)

        self.active_projects: Dict[str, ProjectState] = {}
        self.planner = PlannerAgent()
        self.developer = DeveloperAgent()

        self._load_existing_projects()
        logger.info("Оркестратор инициализирован")

    def _load_existing_projects(self):
        """Загружает существующие проекты при старте"""
        for project_dir in self.projects_root.iterdir():
            if project_dir.is_dir():
                project = ProjectState.load_project(
                    project_dir.name, self.projects_root
                )

                if project:
                    self.active_projects[project.project_name] = project
                    logger.info(f"Загружен проект: {project.project_name}")

    def create_new_project(self, project_name: str, tech_spec: str) -> str:
        """Создает новый проект"""
        normalized_name = self._normalized_project_name(project_name)

        if normalized_name in self.active_projects:
            raise ValueError(f'Проект с именем "{normalized_name}" уже существует')

        project = ProjectState(normalized_name, self.projects_root / normalized_name)
        self.active_projects[normalized_name] = project

        return self._execute_iteration(project, tech_spec)

    def continue_project(self, project_name: str, tech_spec: str) -> str:
        """Продолжает существующий проект"""
        if project_name not in self.active_projects:
            project = ProjectState.load_project(project_name, self.projects_root)

            if not project:
                raise ValueError(f'Проект "{project_name}" не найден')
            self.active_projects[project_name] = project

        project = self.active_projects[project_name]
        return self._execute_iteration(project, tech_spec)

    def _normalized_project_name(self, name: str) -> str:
        """Нормализует название проекта (убирает спецсимволы)"""
        normalized = re.sub(r"[^\w\s-]", "", name)
        normalized = re.sub(r"[-\s]+", "_", normalized)
        return normalized.strip("-_").lower()

    def _execute_iteration(self, project: ProjectState, tech_spec: str) -> str:
        """Выполняет итерацию в проекте"""
        project.start_iteration(tech_spec)

        try:
            plan = self.planner.generate_plan(tech_spec)
            project.update_plan(plan)

            # выполнение задач
            files_changes = self._execute_plan(plan, project)

            project.save_iteration_files(files_changes)
            project.complete_iteration()

            logger.info(
                f'Проект "{project.project_name}" обновлен в итерации {project.iteration}'
            )

        except Exception as e:
            project.status = f"error_iteration_{project.iteration}: {str(e)}"
            logger.error(
                f"Ошибка в итерации {project.iteration} проекта {project.project_name}: {e}"
            )
            logger.exception("")
            raise

        return project.project_name

    def get_project_files(
        self, project_name: str, iteration: Optional[int] = None
    ) -> List[str]:
        """Возвращает файлы проекта"""
        if project_name not in self.active_projects:
            return []

        project = self.active_projects[project_name]

        if iteration:
            # файлы конкретной итерации
            iteration_path = (
                project.iteration_path / f"iteration_{iteration}" / "generated_files"
            )

            if iteration_path.exists():
                return [str(f) for f in iteration_path.rglob("*") if f.is_file()]

            return []
        else:
            return [str(f) for f in project.project_path.rglob("*") if f.is_file()]

    def _execute_plan(self, plan: List[Dict], project: ProjectState) -> Dict[str, str]:
        """Выполняет план задач и возвращает измененя файлов"""
        files_changes = {}
        for task in plan:
            logger.info(f"Обработка задачи {task['id']}")
            result = self.developer.execute_task(task, project)

            # собираем изменения файлов
            if "changes" in result:
                files_changes.update(result["changes"])

            project.status = f"coding_task_{task['id']}_iteration_{project.iteration}"

        return files_changes

    def get_project_status(self, project_name: str) -> Dict[str, Any]:
        """Возвращает статус сессии"""
        if project_name not in self.active_projects:
            return {"error": "Сессия не найдена"}

        return self.active_projects[project_name].get_status()

    def close_session(self, project_name: str) -> bool:
        """Закрывает сессию (и убирает из активных)"""
        if project_name in self.active_projects:
            del self.active_projects[project_name]
            return True
        return False

    def list_projects(self) -> List[Dict[str, Any]]:
        """Возвращает список всех проектов"""
        projects = []

        for project_name, project in self.active_projects.items():
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
