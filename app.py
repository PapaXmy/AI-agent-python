import argparse
import logging

from interfaces.gradio_ui import launch_chat_interface
from utils.config import settings
from utils.loaders import load_documents
from utils.logger_setup import setup_logging
from utils.qa_system import init_qa
from utils.vector_store import delete_project, get_vector_store, list_project

logger = logging.getLogger(__name__)


def main():
    setup_logging()

    logger.info("Запуск AI Code Assistant")

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
    logger.debug(f"Аргументы командной строки: {args}")

    if not settings.openai_api_key:
        error_msg = "OpenAI API ключ не найден"
        logger.error(error_msg)
        print(f"Ошибка: {error_msg}")
        print(
            "Добавте OPENAI_API_KEY в файл .env или установите как переменную окружения"
        )
        return

    if args.list_col:
        logger.info("Запрос списка коллекций")
        projects = list_project()

        if not projects:
            print("Нет созданных коллекций!")
            logger.info("Коллекции не найдены")
        else:
            print("Доступные коллекции:")
            for project in projects:
                print(f" - {project}")
            logger.info(f"Найдено коллекций: {len(projects)}")
        return

    if args.delete_col:
        logger.info(f"Запрос на удаление коллекции: {args.delete_col}")

        if delete_project(args.delete_col):
            print(f'Коллекция "{args.delete_col}" успешно удалена')
            logger.info(f"Коллекция {args.delete_col} удалена")
        else:
            print(f'Коллекция "{args.delete_col}" не найдена')
            logger.warning(f"Коллекция {args.delete_col} не найдена")
        return

    if not args.add_docs and not args.ui:
        logger.info("Вызов справки по использованию")
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
        logger.info(f"Загрузка документов в коллекцию '{args.col}' из {args.add_docs}")
        print(f"Загружаем документы в коллекцию '{args.col}'")
        documents = load_documents(args.add_docs)

        if not documents:
            print("Документы не найдены!")
            logger.warning("Документы не найдены по указанному пути")
            return

        print(f"Найдено {len(documents)} документов.")
        logging.info(f"Загружено {len(documents)} документов.")

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
                logger.debug(
                    f"Документ: {d.metadata.get('file_name', 'Unknow')}, метаданные: {meta_preview}"
                )

    logger.info(f"Инициализация БД для коллекции: {args.col}")
    vector_db = get_vector_store(
        documents=documents if documents else None, project_name=args.col
    )

    qa_chain = init_qa(vector_db)
    logger.info("QA цепочка успешно инициализирована")

    if args.ui:
        logger.info(f"Запуск Gradio UI для коллекции '{args.col}'")
        print(f"Запуск Gradio UI для коллекции '{args.col}'")
        launch_chat_interface()
    else:
        logger.info(f"Документы успешно добавлены в коллекцию {args.col}")
        print(f"Документы успешно добавлены в коллекцию {args.col}")
        print(
            f"Для запуска интерфейса используйте: python app.py --ui --col {args.col}"
        )


if __name__ == "__main__":
    main()
