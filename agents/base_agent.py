import logging

from utils.message_manager import MessageManager
from utils.qa_system import init_qa
from utils.vector_store import get_vector_store

logger = logging.getLogger(__name__)


class BaseAgent:
    def __init__(self, agent_type, collection_name):
        self.agent_type = agent_type
        self.collection_name = collection_name
        self.manager = MessageManager()
        self.qa_chain = None
        self.load_knowledge(collection_name)

    def load_knowledge(self, collection_name):
        """Загрузка базы знаний для агента"""
        try:
            vector_db = get_vector_store(project_name=collection_name)
            self.qa_chain = init_qa(vector_db)
            logger.info(f"Агент {self.agent_type} загрузил коллекцию {collection_name}")
        except Exception as e:
            logger.error(f"Ошибка загрузки коллекции {collection_name}: {e}")
            logger.exception("")

    def process_task(self, task_data):
        """Обработка задачи - должен быть переопределен в дочерних классах"""
        raise NotImplementedError("Метод process_task должен быть реализован")

    def start_listening(self):
        """Запуск прослушивания очереди задач"""
        logger.info(f"Агент {self.agent_type} начал прослушивание очереди")
        while True:
            task = self.manager.get_task(f"queue:{self.agent_type}")
            if task:
                result = self.process_task(task)

                self.manager.send_task(
                    f"queue:next_step",
                    {
                        "from_agent": self.agent_type,
                        "task_id": task.get("task_id"),
                        "result": result,
                    },
                )
