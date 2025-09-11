import argparse
import os

from config import settings
from embeddings import get_embeddings
from interface_gradio import launch_interface
from loaders import load_documents
from qa_system import init_qa
from vector_store import get_vector_store


def main():
    parser = argparse.ArgumentParser(description="AI Code Assistant")
    parser.add_argument(
        "--add-docs", type=str, help="путь к папке с документацией или книгами"
    )
    # parser.add_argument("--project", type=str, help="Название проекта")
    parser.add_argument("--ui", action="store_true", help="Запустить Gradio UI")
    args = parser.parse_args()

    if not settings.openai_api_key:
        print("Ошибка: OpenAI API ключ не найден!")
        print(
            "Добавте OPENAI_API_KEY в файл .env или установите как переменную окружения"
        )
        return

    if not args.add_docs and not args.ui:
        print("Использование:")
        print(" для добавления документов: python app.py --add-docs ./docs")
        print(" Для запуска интерфейса: python app.py --ui")
        return

    documents = []
    if args.add_docs:
        print("Загружаем документы!")
        documents = load_documents(args.add_docs)

        if not documents:
            print("Документы не найдены!")
            return

        print(f"Найдено {len(documents)} документов.")
        for d in documents[:5]:
            meta_preview = {
                k: v
                for k, v in d.metadata.items()
                if k not in ["source", "file_name", "format"]
            }
            print(
                f'-{d.metadata.get("file_name","Unknow")} ({d.metadata.get("format", "Unknow")})'
            )

            if meta_preview:
                print(f" Кастомные метаданные: {meta_preview}")

    vector_db = get_vector_store(documents=documents if documents else None)

    qa_chain = init_qa(vector_db, use_advanced_llm=True)

    if args.ui:
        print("Запуск Gradio UI...")
        launch_interface(qa_chain)
    else:
        print("Документы успешно добавлены в векторную базу.")
        print("Для запуска интерфейса используйте: python app.py --ui")


if __name__ == "__main__":
    main()
