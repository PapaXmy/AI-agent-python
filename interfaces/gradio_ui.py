import logging
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
        with gr.Blocks(title="AutoDevSuite", theme=gr.theme.Soft()) as self.demo:
            gr.Markdown("# AutoDevSuite - AI - агент для генерации кода")

            with gr.Row():
                with gr.Column():
                    tech_spec_input = gr.Textbox(
                        label="Техническое задание",
                        placeholder="Опишите функционал для реализации...",
                        lines=5,
                    )
                    start_btn = gr.Button("Начать сессию", variant="primary")

                with gr.Column():
                    session_id_display = gr.Textbox(
                        label="ID сессии", interactive=False
                    )
                    status_display = gr.Textbox(label="Статус", interactive=False)

            with gr.Row():
                plan_display = gr.JSON(label="План разработки")
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
