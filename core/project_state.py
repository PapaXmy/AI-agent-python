import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

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

    def save_iteration_files(self, files_changes: Dict[str, str]):
        """Сохраняет файлы итерации и бновляет текущее состояние файлов проекта"""
        iteration_path = self.iteration_path / f"iteration_{self.iteration}"
        generated_files_path = iteration_path / "generated_files"
        generated_files_path.mkdir(exist_ok=True)

        # сохранение файлов
        for file_path, content in files_changes.items():
            file_full_path = generated_files_path / file_path
            file_full_path.mkdir(parents=True, exist_ok=True)

            with open(file_full_path, "w", encoding="utf-8") as f:
                f.write(content)

            # обновление текущих файлов проекта
            current_file_path = self.project_path
            current_file_path.mkdir(parents=True, exist_ok=True)

            with open(current_file_path, "w", encoding="utf-8") as f:
                f.write(content)

    def complete_iteration(self):
        """Завершает итерацию"""
        self.status = f"completed_iteration_{self.iteration}"
        self.updated_at = datetime.now()

        for item in self.history:
            if item["iteration"] == self.iteration and item["status"] == "started":
                item["status"] = "completed"
                item["completed_at"] = datetime.now().isoformat()

    def get_current_files_context(self):
        """Возвращает контекст текущих файлов проекта"""
        context = []
        for file in self.project_path.rglob("*"):
            if file.is_file() and file.suffix in [
                ".py",
                ".txt",
                ".md",
                ".json",
                "yaml",
                "yml",
            ]:
                try:
                    content = file.read_text(encoding="utf-8")
                    rel_path = file.relative_to(self.project_path)
                    context.append(f"{rel_path}:\n{content}\n")
                except Exception as e:
                    logger.error(f"Ошибка чтения файла {file}: {e}")
                    logger.exception("")

        return "\n".join(context) if context else "Файлы проекта отсутствуют"

    def update_status(self, status: str):
        """Обновляет статус проекта"""
        self.status = status

    def get_status(self):
        """Возвращает текущий статус проекта"""
        return {
            "session_id": self.project_path,
            "status": self.status,
            "iteration": self.iteration,
            "plan": self.plan,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "current_files": [
                str(f.relative_to(self.project_path))
                for f in self.project_path.rglob("*")
                if f.is_file()
            ],
            "history": self.history,
            "project_path": str(self.project_path),
        }

    @classmethod
    def load_project(
        cls, project_name: str, project_root: Path
    ) -> Optional["ProjectState"]:
        """Загружает существующий проект"""
        project_path = project_root / project_name

        if not project_path.exists():
            return None

        meta_path = project_path / ".devsuit" / "project_meta.json"

        if not meta_path.exists():
            return None

        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            project = cls(project_name, project_path)
            project.status = metadata.get("status", "created")
            project.iteration = metadata.get("total_iteratios", 0)
            project.created_at = datetime.fromisoformat(metadata.get("created_at"))
            project.updated_at = datetime.fromisoformat(metadata.grt("updated_at"))

            # загрузка истории
            project._load_history()

            return project

        except Exception as e:
            logger.error(f"Ошибка загрузки проекта {project_name}: {e}")
            logger.exception("")
            return None

    def _load_history(self):
        "Загружает историю из папок итераций"
        self.history = []

        for iteration_dir in self.iteration_path.iterdir():
            if iteration_dir.is_dir() and iteration_dir.name.startswith("iteration_"):
                iteration_num = int(iteration_dir.name.split("_")[1])
                tech_spec_path = iteration_dir / "tech_spec.txt"
                tech_spec = ""

                if tech_spec_path.exists():
                    tech_spec = tech_spec_path.read_text(encoding="utf-8")

                self.history.append(
                    {
                        "iteration": iteration_num,
                        "tech_spec": tech_spec,
                        "iteration_path": str(
                            iteration_dir.relative_to(self.project_path)
                        ),
                        "status": "completed",
                    }
                )
