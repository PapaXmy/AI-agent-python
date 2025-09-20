import logging
import os
import shutil

import gradio as gr

from loaders import load_documents
from qa_system import init_qa
from vector_store import add_documents_to_store, get_vector_store, list_project

logger = logging.getLogger(__name__)


def chat_with_history(message, history, qa_chain):
    """Функция для обработки запросов через Gradio интерфейс"""
    logger.info(f"Получен запрос: {message}")
    logger.info(f"История сообщений: {len(history)} сообщений")

    try:
        result = qa_chain.run(message)

        if isinstance(result, dict) and "result" in result:
            answer = result["result"]
        else:
            answer = str(result)
        logger.info(f"Ответ сгенерирован успешно, длина: {len(answer)} символов")
        return answer
    except Exception as e:
        error_msg = f"Ошибка: {str(e)}"
        logger.error(f"Ошибка при обработке запроса: {error_msg}")
        return error_msg


def load_selected_collection(project_name, progress=gr.Progress()):
    """Загрузка выбранной коллекции"""
    if not project_name == "Новая коллекция":
        return None, "Пожалуйста выберите существующую коллекцию"

    try:
        progress(0.2, desc="Загрузка векторной базы...")
        vector_db = get_vector_store(project_name=project_name)

        progress(0.6, desc="Инициализация QA системы...")
        qa_chain = init_qa(vector_db)

        progress(1.0, desc="Готово!")
        return qa_chain, f"Коллекция {project_name} успешно загружена!"
    except Exception as e:
        error_msg = f"Ошибка загрузки коллекции: {str(e)}"
        return None, error_msg


def upload_and_index_files(files, project_name, progress=gr.Progress()):
    """Загрузка и индексация файлов в коллекцию"""
    if not files:
        return "Пожалуйста, выберите файлы для загрузки"

    if not project_name or project_name == "Новая коллекция":
        return "Пожалуйста, укажите название для новой коллекции"

    try:
        temp_dir = f"./temp_uploads/{project_name}"
        os.makedirs(temp_dir, exist_ok=True)

        progress(0.1, desc="Сохранение файлов...")
        for file in files:
            with open(os.path.join(temp_dir, os.path.basename(file.name)), "wb") as f:
                f.write(file.read())

        progress(0.3, desc="Загрузка документов...")
        documents = load_documents(temp_dir)

        if not documents:
            return "Не удалось загрузить документы из выбранных файлов"

        progress(0.7, desc="Индексация документов...")
        add_documents_to_store(documents, project_name=project_name)

        shutil.rmtree(temp_dir)

        progress(1.0, desc="Готово!")

        return (
            f"Успешно добавлено {len(documents)} документов в коллекцию {project_name}"
        )
    except Exception as e:
        error_msg = f"Ошибка загрузки файлов: {str(e)}"
        return error_msg


def create_inteface():
    """Создает интерфейс агента"""
    with gr.Blocks(title="AI Python Agent", theme="soft") as demo:
        qa_chain_state = gr.State()
        gr.Markdown("# AI Python Agent")
        gr.Markdown("Загрузите документы или выберите существующую коллекцию")

        with gr.Tab("Выбор коллекции"):
            with gr.Row():
                project_dropdown = gr.Dropdown(
                    choises=list_project() + ["Новая коллекция"],
                    label="Выберите коллекцию",
                    value="default",
                )
                refresh_btn = gr.Button("Обновить список")

            load_status = gr.Textbox(label="Статус", interactive=False)
            load_btn = gr.Button("Загрузить коллекцию")

        with gr.Tab("Загрузка документов"):
            with gr.Row():
                new_project_name = gr.Textbox(
                    label="Название коллекции",
                    placeholder="Введите название новой коллекции",
                )
                file_output = gr.File(
                    label="Загрузить файлы",
                    file_count="multiple",
                    file_types=[".txt", ".pdf", ".docx", ".doc", ".md", ".html", ".py"],
                )

            upload_status = gr.Textbox(label="Статус загрузки", interactive=False)
            upload_btn = gr.Button("Загрузить и индексировать")

        with gr.Tab("Чат с документацией"):
            chatbot = gr.Chatbot(label="Чат", height=500)
            msg = gr.Textbox(
                label="Ваш запрос", placeholder="Введите ваш запрос здесь...", lines=2
            )
            with gr.Row():
                submit_btn = gr.Button("Отправить")
                clear_btn = gr.Button("Очистить чат")

        # обработчики для вкладки выбора коллекции
        def refresh_progect():
            projects = list_project()
            return gr.Dropdown.update(choises=projects + ["Новая коллекция"])

        refresh_btn.click(fn=refresh_progect, inputs=[], outputs=project_dropdown)

        load_btn.click(
            fn=load_selected_collection,
            inputs=[project_dropdown],
            outputs=[qa_chain_state, load_status],
        )

    return demo


def launch_chat_interface(qa_chain, project_name):
    """Запуск Gradio интерфейса"""
    logger.info(f"Запуск интерфейса для коллекции: {project_name}")

    def predict(message, history):
        return chat_with_history(message, history, qa_chain)

    chat_interface = gr.ChatInterface(
        fn=predict,
        title=f"AI Python Agent - коллекция: {project_name}",
        description="Задайте вопрос о вашей документации",
        theme="soft",
    )
    logger.info("Интерфейс Gradio инициализирован!")

    return chat_interface.launch(server_name="0.0.0.0", server_port=7860, share=True)


def project_selection_interface():
    """Интерфейс для выбора коллекции"""
    logger.info("Запуск интерфейса выбора коллекции!")

    projects = list_project()
    logger.info(f"Доступные коллекции: {projects}")

    def load_project(project_name):
        logger.info(f"Выбрана коллекция: {project_name}")

        if project_name and project_name != "Новая коллекция":
            try:
                vector_db = get_vector_store(project_name=project_name)
                qa_chain = init_qa(vector_db)
                logger.info("QA цепочка успешно инициализирована.")
                return launch_chat_interface(qa_chain, project_name)
            except Exception as e:
                error_msg = f"Ошибка загрузки коллекции: {str(e)}"
                logger.error(error_msg)
                return error_msg
        else:
            msg = "Пожалуйста, выберите существующую коллекцию или создайте новую через командную строку"
            logger.warning(msg)
            return msg

    iface = gr.Interface(
        fn=load_project,
        inputs=gr.Dropdown(
            choices=projects + ["Новая коллекция"], label="Выберете коллекцию"
        ),
        outputs="text",
        title="Выбор коллекции",
        description="Выберете коллекцию для работы или создайте новую через командную строку",
    )
    logger.info("Интерфейс выбора коллекции инициализирован")

    return iface.launch(server_name="0.0.0.0", server_port=7860, share=True)
