import json
import logging
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class ProjectState:
    def __init__(self, session_id: str, session_path: Path):
        self.session_id = session_id
        self.session_path = session_path
        self.plan: List[Dict] = []
        self.status = "created"

    def update_plan(self, plan: List[Dict]):
        """Обновляет план проекта"""
        self.plan = plan
        self.status = "planning_complete"

        with open(self.session_path / "plan.json", "w") as f:
            json.dump(plan, f, indent=2)

    def update_status(self, status: str):
        """Обновляет статус проекта"""
        self.status = status

    def get_status(self):
        """Возвращает текущий статус проекта"""
        return {
            "session_id": self.session_id,
            "status": self.status,
            "plan": self.plan,
            "files": list(self.get_project_files()),
        }

    def get_project_files(self):
        """Возвращает список файлов проекта"""
        return self.session_path.rglob("*")
