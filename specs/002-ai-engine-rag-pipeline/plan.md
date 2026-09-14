# Implementation Plan: Motor de IA, Prompts e RAG de Três Passos

**Branch**: `002-ai-engine-rag-pipeline` | **Date**: 2026-09-14 | **Spec**: [specs/002-ai-engine-rag-pipeline/spec.md](spec.md) | **Status**: Completed ✅

## Summary
Implementação do núcleo de inteligência artificial do MigrantIA, incluindo fábrica multi-provedor de LLM, catálogo de prompts multilíngues, orquestrador RAG de 3 passos, busca externa restrita a WhitelistDomain e garantias estritas da Regra de Ouro (Zero Alucinação).

## Technical Context
- **Language/Version**: Python 3.12+ com Type hints completos.
- **Framework**: LangChain 0.3+, Pydantic 2.9+, Django 6.x.
- **Componentes**:
  - `ia/llm/providers.py` e `ia/llm/factory.py`
  - `ia/prompts/system.py`, `ia/prompts/multilingual.py`, `ia/prompts/rag.py`
  - `ia/retrieval/search.py` e `ia/retrieval/filters.py`
  - `ia/rag/chain.py`, `ia/rag/pipeline.py`, `ia/rag/response.py`
- **Testing**: `pytest`, `pytest-django`, mocks e fixtures para simulação de provedores LLM e busca web.

## Planned Steps (Concluídos)
1. **Fábrica LLM (`ia/llm/`)** [CONCLUÍDO ✅]:
   - Factory pattern para instanciar ChatOpenAI, ChatGoogleGenerativeAI ou ChatOllama a partir do `settings.py` / `.env`.
2. **Prompts Multilíngues (`ia/prompts/`)** [CONCLUÍDO ✅]:
   - `MIGRANTIA_SYSTEM_PROMPT` com definição de papel, diretrizes jurídicas, tom humanizado e os 4 pilares.
   - `GOLDEN_RULE_MESSAGES` e templates de resposta para os 5 idiomas principais (`ht`, `fr`, `es`, `en`, `pt`).
3. **Mecanismo de Busca na Whitelist (`ia/retrieval/search.py` & `ia/retrieval/filters.py`)** [CONCLUÍDO ✅]:
   - `WhitelistSearchTool` que constrói a query com os domínios homologados de `WhitelistDomain.objects.filter(is_active=True)`.
4. **Pipeline RAG de 3 Passos (`ia/rag/`)** [CONCLUÍDO ✅]:
   - `RAGPipeline.query(question, ui_language=None)`:
     - 1. Consulta `get_hybrid_retriever` (PostgreSQL/pgvector).
     - 2. Se contexto insuficiente, invoca `WhitelistSearchTool`.
     - 3. Se sem evidências oficiais, aciona a Regra de Ouro.
     - Retorna `RAGResponse(content, sources, language_detected, golden_rule_triggered)`.
5. **Testes Unitários e de Integração** [CONCLUÍDO ✅]:
   - 66 testes automatizados cobrindo todos os provedores, prompts, fluxo de 3 passos e enforcement da Regra de Ouro.
