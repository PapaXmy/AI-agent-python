import argparse

from config import settings
from interface_gradio import launch_interface, project_selection_interface
from loaders import load_documents
from qa_system import init_qa
from vector_store import delete_project, get_vector_store, list_project


def main():
    parser = argparse.ArgumentParser(description="AI Code Assistant")
    parser.add_argument(
        "--add-docs", type=str, help="путь к папке с документацией или книгами"
    )
    parser.add_argument(
        "--col",
        type=str,
        default="default",
        help="Название коллекции (по умолчанию: default)",
    )
    parser.add_argument("--ui", action="store_true", help="Запустить Gradio UI")
    parser.add_argument(
        "--list-col",
        action="store_true",
        help="Показать список всех коллекций в базе данных",
    )
    parser.add_argument(
        "--delete-col", type=str, help="Удатить коллекцию и все ее данные"
    )
    args = parser.parse_args()

    if not settings.openai_api_key:
        print("Ошибка: OpenAI API ключ не найден!")
        print(
            "Добавте OPENAI_API_KEY в файл .env или установите как переменную окружения"
        )
        return

    if args.list_col:
        projects = list_project()

        if not projects:
            print("Нет созданных коллекций!")
        else:
            print("Доступные проекты:")
            for project in projects:
                print(f" - {project}")
        return

    if args.delete_col:

        if delete_project(args.delete_col):
            print(f'Коллекция "{args.delete_col}" успешно удалена')
        else:
            print(f'Коллекция "{args.delete_col}" не найдена')
        return

    if not args.add_docs and not args.ui:
        print("Использование:")
        print(
            " для добавления документов: python app.py --add-docs ./docs --col <my collection>"
        )
        print(" Для запуска интерфейса: python app.py --ui --col <my collection>")
        print(" Для показа списка коллекций: python app.py --list-col")
        print(" Для удаления коллекции: python app.py --delete_col <my collection>")
        return

    documents = []
    if args.add_docs:
        print(f"Загружаем документы в коллекцию '{args.col}'")
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

    vector_db = get_vector_store(
        documents=documents if documents else None, project_name=args.col
    )

    qa_chain = init_qa(vector_db)

    if args.ui:
        print(f"Запуск Gradio UI для коллекции '{args.col}'")
        launch_interface(qa_chain, args.col)
    else:
        print(f"Документы успешно добавлены в коллекцию {args.col}")
        print(
            f"Для запуска интерфейса используйте: python app.py --ui --col {args.col}"
        )


if __name__ == "__main__":
    main()
