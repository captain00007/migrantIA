"""
Módulo de Intenção e Roteamento Semântico do MigrantIA.
Define as categorias conceituais de intenção de consultas.
"""
from enum import Enum


class QueryIntent(str, Enum):
    """Categorias conceituais de intenção de mensagens."""
    KNOWLEDGE_QUERY = "knowledge_query"      # Dúvidas procedimentais, documentais ou de direitos
    CHITCHAT_GREETING = "chitchat_greeting"  # Saudações vazias ou interações não-procedimentais
    OUT_OF_SCOPE = "out_of_scope"            # Temas flagrantemente fora dos 4 Pilares


class IntentClassifier:
    """
    Classificador de intenção de mensagens baseado em delegação semântica universal.
    Elimina listas hardcoded de idiomas específicos, permitindo que qualquer idioma do mundo
    (Sesotho, Iorubá, Lingala, Árabe, Kreyòl, etc.) seja interpretado de forma nativa e contextual pelo LLM.
    """

    @classmethod
    def classify(cls, text: str) -> QueryIntent:
        """
        Classifica a intenção de forma universal.
        Consultas com conteúdo são encaminhadas ao pipeline semântico universal,
        onde o LLM, o histórico (chat_history) e o ContextShield decidem a resposta.
        """
        if not text or not text.strip():
            return QueryIntent.CHITCHAT_GREETING

        return QueryIntent.KNOWLEDGE_QUERY
