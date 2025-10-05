import logging
from pathlib import Path

import gradio as gr

from core.orchestrator import Orchestrator

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
                self.continue_project,
                inputs=[project_selector, new_tech_spec],
                outputs=[project_status, project_history, project_files],
            )
            project_selector.change(
                self.load_project_info,
                inputs=project_selector,
                outputs=[
                    project_status,
                    project_history,
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

    def toggle_file_version(self, file_version, project_selector):
        """Пререключает между текущими файлами и файлами итерации"""
        if not project_selector:
            return gr.Dropdown(visible=False, choices=[]), None

        project_name = self._extract_project_name(project_selector)
        if file_version == "По итерациям":
            status = self.orchestrator.get_project_status(project_name)
            iterations = [
                f"Итерация {item['iteration']}" for item in status.get("history", [])
            ]
            return gr.Dropdown(visible=True, choices=iterations), None
        else:
            files = self.orchestrator.get_project_files(project_name)
            return gr.Dropdown(visible=False, choices=[]), files

    def load_iteration_files(self, project_selector, iteration_selector):
        """Загружает файлы конкретной итерации"""
        if not project_selector or not iteration_selector:
            return None

        project_name = self._extract_project_name(project_selector)
        iteration_num = int(iteration_selector.split(" ")[1])

        files = self.orchestrator.get_project_files(project_name, iteration_num)
        return files

    def refresh_sessions(self):
        """Обновление сессий"""
        choices = self._get_project_choises()
        return gr.update(choices=choices, value=choices[0] if choices else None)

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

    def run(self, server_name="0.0.0.0", server_port=7860, share=False):
        """Запуск приложения"""
        logger.info("Запуск AutoDevSuite")
        self.demo.launch(
            server_name=server_name,
            server_port=server_port,
            share=share,
            show_error=True,
        )
