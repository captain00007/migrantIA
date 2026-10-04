"""
Cadeia LangChain para geração de respostas fundamentadas no contexto oficial.
"""
from typing import Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSerializable
from ia.llm.factory import get_llm
from ia.prompts.rag import get_rag_prompt_template


def create_rag_chain(
    llm: Optional[BaseChatModel] = None,
) -> RunnableSerializable:
    """
    Cria a cadeia de processamento RAG: Prompt -> LLM -> StrOutputParser.
    """
    active_llm = llm or get_llm(temperature=0.3)
    prompt = get_rag_prompt_template()
    return prompt | active_llm | StrOutputParser()
