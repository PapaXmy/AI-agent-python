import logging

import gradio as gr

from qa_system import init_qa
from vector_store import get_vector_store, list_project

logger = logging.getLogger(__name__)


def chat(query, qa_chain):
    """Функция для обработки запросов через Gradio интерфейс"""
    logger.info(f"Получен запрос: {query}")

    try:
        result = qa_chain.invoke({"query": query})

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


def launch_interface(qa_chain, project_name):
    """Функция которая запускает Gradio интерфейс"""
    logger.info(f"Запуск интерфейса для коллекции: {project_name}")
    iface = gr.Interface(
        fn=lambda query: chat(query, qa_chain),
        inputs="text",
        outputs="text",
        title=f"AI Python Agent - коллекция: {project_name}",
        description="Задайте вопрос о вашей документации",
    )
    logger.info("Интерфейс Gradio инициализирован!")

    return iface.launch(server_name="0.0.0.0", server_port=7860, share=True)


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
                return launch_interface(qa_chain, project_name)
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
