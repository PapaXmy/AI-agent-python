import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class ProjectState:
    def __init__(self, session_id: str, session_path: Path):
        self.session_id = session_id
        self.session_path = session_path
        self.plan: List[Dict] = []
        self.status = "created"
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.iteration = 0
        self.history: List[Dict]

    def start_iteration(self, tech_spec: str):
        """Начинает итерацию"""
        self.iteration += 1
        self.status = f"iteration_{self.iteration}"
        self.updated_at = datetime.now()

        self.history.append(
            {
                "iteration": self.iteration,
                "tech_spec": tech_spec,
                "timestamp": self.updated_at.isoformat(),
                "status": "started",
            }
        )

        tech_spec_path = self.session_path / f"tech_spec_iteration_{self.iteration}.txt"
        with open(tech_spec_path, "w", encoding="utf-8") as f:
            f.write(tech_spec)

    def update_plan(self, plan: List[Dict]):
        """Обновляет план проекта"""
        self.plan = plan
        self.status = f"planning_complete_iteration_{self.iteration}"

        plan_path = self.session_path / f"plan_iteration_{self.iteration}.json"
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
