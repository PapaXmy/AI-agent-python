import logging
import os
import shutil

import gradio as gr

from loaders import load_documents
from qa_system import init_qa
from vector_store import (
    add_documents_to_store,
    delete_project,
    get_vector_store,
    list_project,
)

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
        logger.exception("Текст ошибки")
        logger.error(f"Ошибка при обработке запроса: {error_msg}")
        return error_msg


def load_selected_collection(project_name, progress=gr.Progress()):
    """Загрузка выбранной коллекции"""
    # if not project_name == "Новая коллекция":
    #     return None, "Пожалуйста выберите существующую коллекцию"

    try:
        progress(0.2, desc="Загрузка векторной базы...")
        vector_db = get_vector_store(project_name=project_name)

        progress(0.6, desc="Инициализация QA системы...")
        qa_chain = init_qa(vector_db)

        progress(1.0, desc="Готово!")
        logger.info(f"Коллекция {project_name} успешно загружена")
        return qa_chain, f"Коллекция {project_name} успешно загружена!"
    except Exception as e:
        error_msg = f"Ошибка загрузки коллекции: {str(e)}"
        logger.error(error_msg)
        return None, error_msg


def upload_and_index_files(files, project_name, progress=gr.Progress()):
    """Загрузка и индексация файлов в коллекцию"""
    if not files:
        return "Пожалуйста, выберите файлы для загрузки"

    # if not project_name or project_name == "Новая коллекция":
    #     return "Пожалуйста, укажите название для новой коллекции"

    try:
        temp_dir = f"./temp_uploads/{project_name}"
        os.makedirs(temp_dir, exist_ok=True)

        progress(0.1, desc="Сохранение файлов...")
        for file in files:
            try:
                file_name = os.path.basename(file.name)
                file_path = os.path.join(temp_dir, file_name)

                shutil.copyfile(file.name, file_path)
                logger.info(f"Файл {file_name} успешно скопирован")
            except Exception as e:
                logger.error(f"Ошибка при обработке файла {file.name}")
                logger.error(f"Тип объекта: {type(file)}")
                logger.error(f"Атрибуты объекта: {dir(file)}")
                logger.exception("Полный текст ошибки")
                continue

        progress(0.3, desc="Загрузка документов...")
        documents = load_documents(temp_dir)

        if not documents:
            return "Не удалось загрузить документы из выбранных файлов"

        progress(0.7, desc="Индексация документов...")
        add_documents_to_store(documents, project_name=project_name)

        shutil.rmtree(temp_dir)

        progress(1.0, desc="Готово!")
        logger.info(f"Вколлекци {project_name} добавлено {len(documents)} документов")
        return (
            f"Успешно добавлено {len(documents)} документов в коллекцию {project_name}"
        )
    except Exception as e:
        error_msg = f"Ошибка загрузки файлов: {str(e)}"
        logger.exception("Ошибка загрузки файлов")
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
                    choices=list_project(),
                    label="Выберите коллекцию",
                    value="default",
                )
                refresh_btn = gr.Button("Обновить список")
                delete_btn = gr.Button("Удалить выбранную коллекцию")
            with gr.Row():
                new_project_name = gr.Textbox(
                    label="Название коллекции",
                    placeholder="Введите название новой коллекции",
                )
                create_project = gr.Button("Создать новую коллекцию")

            load_status = gr.Textbox(label="Статус", interactive=False)
            load_btn = gr.Button("Загрузить коллекцию")

        with gr.Tab("Загрузка документов"):
            with gr.Row():
                project_dropdown_name = gr.Dropdown(
                    choices=list_project(),
                    label="Выберите коллекцию",
                    value="default",
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
            return gr.Dropdown(choices=projects)

        refresh_btn.click(fn=refresh_progect, inputs=[], outputs=project_dropdown)
        create_project.click(fn=get_vector_store, inputs=[new_project_name])
        delete_btn.click(fn=delete_project, inputs=[project_dropdown])
        load_btn.click(
            fn=load_selected_collection,
            inputs=[project_dropdown],
            outputs=[qa_chain_state, load_status],
        )

        # обработчик для вкладки загрузки документов
        upload_btn.click(
            fn=upload_and_index_files,
            inputs=[file_output, project_dropdown_name],
            outputs=upload_status,
        )

        # обработчик чата
        def respond(message, chat_history, qa_chain):
            if qa_chain is None:
                chat_history.append(
                    (
                        message,
                        'Сначала загрузите коллекцию из вкладки "выбор коллекции"',
                    )
                )

                return "", chat_history

            answer = chat_with_history(message, chat_history, qa_chain)
            chat_history.append((message, answer))
            return "", chat_history

        msg.submit(respond, [msg, chatbot, qa_chain_state], [msg, chatbot])
        submit_btn.click(respond, [msg, chatbot, qa_chain_state], [msg, chatbot])

        clear_btn.click(lambda: None, None, chatbot, queue=False)

    return demo


def launch_chat_interface():
    """Запуск Gradio интерфейса"""
    demo = create_inteface()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=True)
