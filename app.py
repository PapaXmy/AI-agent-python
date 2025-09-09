import argparse

from config import settings
from embeddings import get_embeddings
from interface_gradio import chat
from loaders import load_documents
from qa_system import init_qa
from vector_store import get_vector_store


def main():
    parser = argparse.ArgumentParser(description="AI Code Assistant")
    parser.add_argument(
        "--add-docs", type=str, help="путь к папке с документацией или книгами"
    )
    parser.add_argument("--project", type=str, help="Название проекта")
    parser.add_argument("--ui", action="store_true", help="Запустить Gradio UI")
    args = parser.parse_args()

    if not args.add_docs:
        print("Укажите путь к документам через --add-docs ./docs")
        return

    print("Загружаем документы")
    documents = load_documents(args.add_docs)

    if not documents:
        print("Документы не найдены!")

    print(f"Найдено {len(documents)} документов.")
    for d in documents[:5]:
        meta_preview = {
            k: v
            for k, v in d.metadata.items()
            if k not in ["source", "file_name", "format"]
        }
        print(f'-{d.metadata["file_name"]} ({d.metadata["format"]})')

        if meta_preview:
            print(f"Кастомные метаданные: {meta_preview}")

    embeddings = get_embeddings(use_openai=True)

    vector_db = get_vector_store(documents, embeddings)

    qa_chain = init_qa(vector_db, use_advanced_llm=True)

    if args.ui:
        print("Запуск Gradio UI...")
        interface = chat(qa_chain)
        interface.launch(server_name="0.0.0.0", server_port=7860, share=True)


if __name__ == "__main__":
    main()
