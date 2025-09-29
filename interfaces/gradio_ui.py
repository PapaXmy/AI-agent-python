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
            gr.Markdown("# AutoDevSuite - AI - агент для генерации кода")

            with gr.Row():
                with gr.Column():
                    session_selector = gr.Dropdown(
                        label="Выберите сессию для продолжения",
                        choices=[],
                        allow_custom_value=True,
                        # placeholder="Оставте пустым для новой сессии...",
                    )

                    tech_spec_input = gr.Textbox(
                        label="Техническое задание",
                        placeholder="Опишите функционал для реализации...",
                        lines=5,
                    )

                    with gr.Row():

                        start_btn = gr.Button("Начать сессию", variant="primary")
                        continue_btn = gr.Button(
                            "Продолжить сессию", variant="secondary"
                        )
                        close_btn = gr.Button("Закрыть сессию", variant="stop")

                with gr.Column():
                    session_id_display = gr.Textbox(
                        label="ID сессии", interactive=False
                    )
                    status_display = gr.Textbox(label="Статус", interactive=False)
                    iteration_display = gr.Textbox(label="Итерация", interactive=False)

            with gr.Row():
                with gr.Column():
                    gr.Markdown("План разработки")
                    plan_display = gr.JSON(label="Сгенерированный план")

                with gr.Column():
                    gr.Markdown("История изменений")
                    history_display = gr.JSON(label="История сессии")

            with gr.Row():
                gr.Markdown("Файлы проекта")
                files_display = gr.File(label="Файлы проекта", file_count="multiple")

            # обработчик событий
            start_btn.click(
                self.start_session,
                inputs=tech_spec_input,
                outputs=[
                    session_id_display,
                    status_display,
                    plan_display,
                    files_display,
                ],
            )
            continue_btn.click(
                self.continue_session,
                inputs=[session_selector, tech_spec_input],
                outputs=[
                    session_id_display,
                    status_display,
                    plan_display,
                    history_display,
                    files_display,
                    iteration_display,
                ],
            )
            close_btn.click(
                self.close_session,
                inputs=[session_selector],
                outputs=[session_id_display, status_display, session_selector],
            )

    def continue_session(self, session_selector, tech_spec):
        """Продолжает существующую сессию"""
        if not tech_spec.strip():
            return "", "Ошибка: ТЗ не может быть пустым", "", None, None, None

        session_id = self.extract_session_id(session_selector)
        if not session_id:
            return "", "Ошибка выберите сессию для продолжения", "", None, None, None

        try:
            session_id = self.orchestrator.continue_session(session_id, tech_spec)
            status = self.orchestrator.get_session_status(session_id)

            return (
                session_id,
                status.get("status", "unknown"),
                f'Итерация {status.get("iteration", 0)}',
                status.get("paln", []),
                status.get("history", []),
                self.get_session_files(session_id),
            )

        except Exception as e:
            logger.error(f"Ошибка продолжения сессии: {e}")
            logger.exception("")
            return "", f"Ошибка: {str(e)}", "", None, None, None

    def extract_session_id(self, session_selector):
        """Извлекает session_id из значения селектора"""
        pass

    def close_session(self):
        """Закрывает сессию"""
        pass

    def start_session(self, tech_spec):
        """Запускает новую сессию"""
        if not tech_spec.strip():
            return "", "Ошибка: ТЗ не может быть пустым", None, None, None

        try:
            session_id = self.orchestrator.start_new_session(tech_spec)
            status = self.orchestrator.get_session_status(session_id)

            return (
                session_id,
                status.get("status", "unknow"),
                f'Итерация {status.get("iteration", 0)}',
                status.get("plan", []),
                status.get("history", []),
                self.get_session_files(session_id),
            )

        except Exception as e:
            logger.error(f"Ошибка запуска сессии: {e}")
            logger.exception("")
            return "", f"Ошибка: {str(e)}", None, None, None

    def get_session_files(self, session_id):
        """Возвращает файлы файлы сессии"""
        if not session_id:
            return None

        session_path = Path(f"./projects/{session_id}")
        return [str(f) for f in session_path.rglob("*") if f.is_file()]

    def run(self):
        """Запуск приложенгия"""
        logger.info("Запуск AutoDevSuite")
        self.demo.launch(server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    app = AutoDevSuiteUI()
    app.run
