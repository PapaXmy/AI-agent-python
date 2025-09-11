import gradio as gr


def chat(query, qa_chain):
    """Функция для обработки запросов через Gradio интерфейс"""
    try:
        result = qa_chain.run(query)
        return result
    except Exception as e:
        return f"Ошибка: {str(e)}"


iface = gr.Interface(fn=chat, inputs="text", outputs="text", title="AI Freelance Agent")

iface.launch()
