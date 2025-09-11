import gradio as gr


def chat(query, qa_chain):
    """Функция для обработки запросов через Gradio интерфейс"""
    try:
        result = qa_chain.run(query)
        return result
    except Exception as e:
        return f"Ошибка: {str(e)}"


def launch_interface(qa_chain):
    """Функция которая запускает Gradio интерфейс"""
    iface = gr.Interface(
        fn=lambda query: chat(query, qa_chain),
        inputs="text",
        outputs="text",
        title="AI Python Agent",
        description="Задайте вопрос о вашей документации",
    )

    return iface.launch(server_name="0.0.0.0", server_port=7860, share=True)
