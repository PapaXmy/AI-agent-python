import logging

from utils.rag_manager import RAGManager

logger = logging.getLogger(__name__)


class BaseAgent:
    def __init__(self, agent_type: str, project_name: str = "default"):
        self.agent_type = agent_type
        self.project_name = project_name
        self.rag_manager = RAGManager(project_name)
        logger.info(f"Агент {agent_type} инициализирован")

    def get_rag_context(self, query: str, max_docs: int = 3) -> str:
        """Получает контекст из RAG системы"""
        return self.rag_manager.get_context(query, max_docs)
