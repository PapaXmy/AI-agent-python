import logging
from pathlib import Path

import gradio as gr

from core.orchestrator import Orchestrator
from utils.logger_setup import setup_logging

logger = logging.getLogger(__name__)


class AutoDevSuiteUI:
    """Класс управления Gradio интерфейсом"""

    def __init__(self):
        self.orchestrator = Orchestrator()
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс Gradio"""
        with gr.Blocks(title="AutoDevSuite", theme="soft") as self.demo:
            gr.Markdown("# AutoDevSuite - Управление проектами")

            with gr.Row():
                with gr.Column(scale=2):
                    # создание проектов
                    with gr.Group():
                        gr.Markdown("Создать новый проект")
                        new_project_name = gr.Textbox(
                            label="Название пректа",
                            info="Используйте английские буквы, цифры и подчеркивания",
                        )
                        new_tech_spec = gr.Textbox(
                            label="Техническое задание",
                            placeholder="Опишите функционал для реализации",
                            lines=4,
                        )

                        create_btn = gr.Button("Создать проект", variant="primary")

                with gr.Column(scale=1):
                    # управление существующими проектами
                    with gr.Group():
                        gr.Markdown("Проекты")
                        project_selector = gr.Dropdown(
                            label="Выберите проект",
                            choices=self._get_project_choises(),
                            allow_custom_value=False,
                        )
                        refresh_btn = gr.Button("Обновить список", size="sm")
                        continue_btn = gr.Button(
                            "Доработать проект", variant="secondary"
                        )

            # статус и информация
            with gr.Row():
                with gr.Column():
                    project_status = gr.JSON(label="Статус проекта")

                with gr.Column():
                    project_history = gr.JSON(label="История итераций")

            # файлы проекта
            with gr.Row():
                gr.Markdown("Файлы проекта")

            with gr.Row():
                file_version = gr.Radio(
                    choices=["Текущие файлы", "По итерациям"],
                    label="Версия файлов",
                    value="Текущие файлы",
                )
                iteration_selector = gr.Dropdown(
                    label="Выберите итерацию",
                    choices=[],
                    interactive=True,
                    visible=False,
                )

            project_files = gr.File(label="Файлы проекта", file_count="multiple")

            # обработчик событий
            refresh_btn.click(self.refresh_sessions, outputs=project_selector)
            create_btn.click(
                self.create_project,
                inputs=[new_project_name, new_tech_spec],
                outputs=[project_status, project_history, project_files],
            )
            continue_btn.click(
                self.continue_session,
                inputs=[project_selector, project_history, project_files],
                outputs=[project_status, project_history, project_files],
            )
            project_selector.change(
                self.load_project_info,
                inputs=project_selector,
                outputs=[
                    project_status,
                    project_status,
                    project_files,
                    iteration_selector,
                ],
            )
            file_version.change(
                self.toggle_file_version,
                inputs=[file_version, project_selector],
                outputs=[iteration_selector, project_files],
            )
            iteration_selector.change(
                self.load_iteration_files,
                inputs=[project_selector, iteration_selector],
                outputs=project_files,
            )

    def create_project(self, project_name, tech_spec):
        """Создает новый проект"""
        if not project_name.strip():
            return {"error": "Введите название проекта"}, [], None

        if not tech_spec.strip():
            return {"error": "Введите техническое задание"}, [], None

        try:
            project_id = self.orchestrator.create_new_project(project_name, tech_spec)
            status = self.orchestrator.get_project_status(project_id)
            files = self.orchestrator.get_project_files(project_id)

            return status, status.get("history", []), files

        except Exception as e:
            logger.error(f"Ошибка создания проекта: {e}")
            logger.exception("")
            return {"error": str(e)}, [], None

    def load_project_info(self, project_selector):
        """Загружает информацию о проекте"""
        if not project_selector:
            return {}, [], None, gr.Dropdown(choices=[])

        project_name = self._extract_project_name(project_selector)
        status = self.orchestrator.get_project_status(project_name)

        # список итераций для выбора
        iterations = []
        if "history" in status:
            iterations = [f"Итерация {item['iteration']}" for item in status["history"]]

        files = self.orchestrator.get_project_files(project_name)

        return status, status.get("history", []), files, gr.Dropdown(choices=iterations)

    def toggle_file_version(self):
        pass

    def load_iteration_files(self):
        pass

    def refresh_sessions(self):
        """Обновление сессий"""
        choices = self._get_project_choises()
        return gr.Dropdown(choices=choices, value=choices[0] if choices else None)

    def _get_project_choises(self):
        """Возвращает список проектов для выбора"""
        projects = self.orchestrator.list_projects()
        return [f"{p['project_name']} (итерация {p['iteration']})" for p in projects]

    def continue_project(self, project_selector, tech_spec):
        """Продолжает существующий проект"""
        if not project_selector:
            return {"error": "Выберите проект"}, [], None
        if not tech_spec.strip():
            return {"error": "Введите описание доработки"}, [], None

        project_name = self._extract_project_name(project_selector)

        try:
            project_id = self.orchestrator.continue_project(project_name, tech_spec)
            status = self.orchestrator.get_project_status(project_id)
            files = self.orchestrator.get_project_files(project_id)

            return status, status.get("history", []), files
        except Exception as e:
            logger.error(f"Ошибка продолжения проекта: {e}")
            logger.exception("")
            return f"Ошибка: {str(e)}", [], None

    def _extract_project_name(self, selector_value):
        """Извлекает название из значения селектора"""
        if selector_value:
            return selector_value.split(" ")[0]
        return None

    def close_session(self, session_selector):
        """Закрывает сессию"""
        session_id = self.extract_session_id(session_selector)
        if not session_id:
            return "", "Ошибка выберите сессию", ""

        try:
            success = self.orchestrator.close_session(session_id)

            if success:
                return "", f"Сессия {session_id} закрыта", ""
            else:
                return "", f"Ошибка закрытия сессии {session_id}", ""

        except Exception as e:
            logger.error(f"Ошибка закрытия сессии {session_id}")
            logger.exception("")
            return "", f"Ошибка: {str(e)}", ""

    # def create_project(self, tech_spec):
    #     """Запускает новую сессию"""
    #     if not tech_spec.strip():
    #         return "", "Ошибка: ТЗ не может быть пустым", None, None, None
    #
    #     try:
    #         session_id = self.orchestrator.start_new_session(tech_spec)
    #         status = self.orchestrator.get_session_status(session_id)
    #
    #         return (
    #             session_id,
    #             status.get("status", "unknow"),
    #             f"Итерация {status.get('iteration', 0)}",
    #             status.get("plan", []),
    #             status.get("history", []),
    #             self.get_session_files(session_id),
    #         )
    #
    #     except Exception as e:
    #         logger.error(f"Ошибка запуска сессии: {e}")
    #         logger.exception("")
    #         return "", f"Ошибка: {str(e)}", None, None, None
    #
    def get_session_files(self, session_id):
        """Возвращает файлы файлы сессии"""
        if not session_id:
            return None

        session_path = Path(f"./projects/{session_id}")

        if session_path.exists():
            return [str(f) for f in session_path.rglob("*") if f.is_file()]
        return None

    def run(self, server_name="0.0.0.0", server_port=7860, share=False):
        """Запуск приложения"""
        logger.info("Запуск AutoDevSuite")
        self.demo.launch(
            server_name=server_name,
            server_port=server_port,
            share=share,
            show_error=True,
        )


# if __name__ == "__main__":
#     app = AutoDevSuiteUI()
#     app.run
