import gradio as gr

from qa_system import init_qa
from vector_store import get_vector_store, list_project


def chat(query, qa_chain):
    """Функция для обработки запросов через Gradio интерфейс"""
    try:
        result = qa_chain.invoke({"query": query})
        return result
    except Exception as e:
        return f"Ошибка: {str(e)}"


def launch_interface(qa_chain, project_name):
    """Функция которая запускает Gradio интерфейс"""
    iface = gr.Interface(
        fn=lambda query: chat(query, qa_chain),
        inputs="text",
        outputs="text",
        title=f"AI Python Agent - коллекция: {project_name}",
        description="Задайте вопрос о вашей документации",
    )

    return iface.launch(server_name="0.0.0.0", server_port=7860, share=True)


def project_selection_interface():
    """Интерфейс для выбора коллекции"""
    projects = list_project()

    def load_project(project_name):
        if project_name and project_name != "Новая коллекция":
            vector_db = get_vector_store(project_name=project_name)
            qa_chain = init_qa(vector_db)
            return launch_interface(qa_chain, project_name)
        else:
            return "Пожалуйста, выберите существующий проект или создайте новый через командную строку"

    iface = gr.Interface(
        fn=load_project,
        inputs=gr.Dropdown(
            choices=projects + ["Новая коллекция"], label="Выберете коллекцию"
        ),
        outputs="text",
        title="Выбор коллекции",
        description="Выберете коллекцию для работы или создайте новую через командную строку",
    )

    return iface.launch(server_name="0.0.0.0", server_port=7860, share=True)
