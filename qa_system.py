from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.llms import HuggingFaceHub
from langchain_openai import ChatOpenAI
from openai import OpenAI

from config import settings
from vector_store import get_vector_store


def init_qa(vector_db, use_advanced_llm: bool = True, model_name="gpt-5"):
    retriever = vector_db.as_retriever()

    if use_advanced_llm:
        if not settings.openai_api_key:
            raise ValueError("Не найден OpenAI API ключ, проверте ваш .env файл")

        client = OpenAI(
            api_key=settings.openai_api_key, base_url=settings.openai_base_url
        )

        class CustomOpenAIWrapper:
            def __init__(self, client, model_name):
                self.client = client
                self.model_name = model_name

            def invoke(self, prompt):
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=2000,
                )
                return response.choise[0].message.content

        llm = CustomOpenAIWrapper(client, model_name)

        # openai_kwargs = {
        #     "model": model_name,
        #     "temperature": 0.1,
        #     "max_tokens": 2000,
        #     "openai_api_key": settings.openai_api_key,
        # }
        #
        # if settings.openai_base_url:
        #     openai_kwargs["openai_base_url"] = settings.openai_base_url
        #
        # llm = ChatOpenAI(**openai_kwargs)
    else:
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

    return RetrievalQA.from_chain_type(
        llm=llm, retriever=retriever, chain_type_kwargs={"prompt": prompt}
    )
