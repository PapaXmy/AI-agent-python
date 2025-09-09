import gradio as gr

from qa_system import init_qa

qa = init_qa()


def chat(query):
    return qa.run(query)


iface = gr.Interface(fn=chat, inputs="text", outputs="text", title="AI Freelance Agent")

iface.launch()
