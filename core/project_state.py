import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class ProjectState:
    def __init__(self, project_name: str, project_path: Path):
        self.project_name = project_name
        self.project_path = project_path
        self.hidden_dir_path = project_path / ".devsuit"
        self.iteration_path = self.hidden_dir_path / "iteration"
        self.meta_path = self.hidden_dir_path / "poject_meta.json"

        self.plan: List[Dict] = []
        self.status = "created"
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.iteration = 0
        self.history: List[Dict] = []

        self._initialize_project_structure()

    def _initialize_project_structure(self):
        """Создает структуру папок для проекта"""
        self.hidden_dir_path.mkdir(parents=True, exist_ok=True)
        self.iteration_path.mkdir(parents=True, exist_ok=True)

        if not self.meta_path.exists():
            self._save_metadata()

    def _save_metadata(self):
        """Сохраняет метаданные проекта"""
        metadata = {
            "project_name": self.project_name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "total_iteratios": self.iteration,
            "status": self.status,
        }

        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def start_iteration(self, tech_spec: str):
        """Начинает итерацию"""
        self.iteration += 1
        self.status = f"iteration_{self.iteration}"
        self.updated_at = datetime.now()

        iteration_path = self.iteration_path / f"iteration_{self.iteration}"
        iteration_path.mkdir(exist_ok=True)

        tech_spec_path = iteration_path / "tech_spec.txt"
        with open(tech_spec_path, "w", encoding="utf-8") as f:
            f.write(tech_spec)

        self.history.append(
            {
                "iteration": self.iteration,
                "tech_spec": tech_spec,
                "timestamp": self.updated_at.isoformat(),
                "status": "started",
                "iteration_path": str(iteration_path.relative_to(self.project_path)),
            }
        )

        self._save_metadata()

    def update_plan(self, plan: List[Dict]):
        """Обновляет план проекта"""
        self.plan = plan
        self.status = f"planning_complete_iteration_{self.iteration}"

        iteration_path = self.iteration_path / f"iteration_{self.iteration}"
        plan_path = iteration_path / "plan.json"

        with open(plan_path, "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)

    def complete_iteration(self):
        """Завершает итерацию"""
        self.status = f"completed_iteration_{self.iteration}"
        self.updated_at = datetime.now()

        for item in self.history:
            if item["iteration"] == self.iteration and item["status"] == "started":
                item["status"] = "completed"
                item["completed_at"] = datetime.now().isoformat()

    def update_status(self, status: str):
        """Обновляет статус проекта"""
        self.status = status

    def get_status(self):
        """Возвращает текущий статус проекта"""
        return {
            "session_id": self.session_id,
            "status": self.status,
            "iteration": self.iteration,
            "plan": self.plan,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "files": [
                str(f.relative_to(self.session_path))
                for f in self.session_path.rglob("*")
                if f.is_file()
            ],
            "history": self.history,
        }
