import logging

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.llms import HuggingFaceHub
from langchain_openai import ChatOpenAI

from config import settings

logger = logging.getLogger(__name__)


def init_qa(vector_db, use_advanced_llm: bool = True, model_name="gpt-5"):
    """Инициализация QA системы (вопрос/ответ LLM)"""
    logger.info("Инициализация QA системы")
    retriever = vector_db.as_retriever()
    logger.debug("Retriever создан")

    if use_advanced_llm:

        if not settings.openai_api_key:
            error_msg = "Не найден OpenAI API ключ, проверте ваш .env файл"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info(f"Использованеи OpenAI модели: {model_name}")
        llm = ChatOpenAI(
            model=model_name,
            temperature=0.1,
            max_tokens=2000,
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.openai_api_base,
        )
    else:
        logger.info("Использованте локальной модели HuggingFace")
        llm = HuggingFaceHub(
            repo_id="google/flan-t5-large",
            model_kwargs={"temperature": 0.1, "max_length": 1000},
        )

    prompt_template = """Ты - AI-Python разработчик. Используй контекст, 
    чтобы отвечать максимально полезно.

    Контекст:
    {context}

    Вопрос:
    {question}

    Ответ:"""

    prompt = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    logger.info("QA система успешно инициализирована")
    return RetrievalQA.from_chain_type(
        llm=llm, retriever=retriever, chain_type_kwargs={"prompt": prompt}
    )
