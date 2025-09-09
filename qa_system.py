from langchain.chain import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.llm import HuggingFaceHub
from langchain_openai import ChatOpenAI

from config import settings
from vector_store import get_vector_store


def init_qa(use_advanced_llm: bool = True, model_name="gpt-5"):
    vectordb = get_vector_store()
    retriever = vectordb.as_retriever()

    if use_advanced_llm:
        llm = ChatOpenAI(
            model=model_name,
            temperature=0.1,
            max_tokens=2000,
            open_api_key=settings.open_api_key,
            open_api_base=settings.open_base_url,
        )
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
        template=prompt_template, input_variables=["contex", "question"]
    )

    return RetrievalQA.from_chain_type(
        llm=llm, retriever=retriever, chain_type_kwargs={"prompt": prompt}
    )
