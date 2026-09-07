# Implementation Plan: Chat de Orientação e Consulta Multilíngue para Migrantes (Quatro Pilares)

**Branch**: `001-multilingual-migrant-chat` | **Date**: 2026-09-05 | **Spec**: [specs/001-multilingual-migrant-chat/spec.md](spec.md)

**Input**: Feature specification from `specs/001-multilingual-migrant-chat/spec.md`

## Summary

Implementação do sistema conversacional e da interface web/PWA do MigrantIA com suporte integral aos **Quatro Pilares de Conhecimento** (Imigração e Regularização, Estudo e Educação, Nacionalidade e Naturalização, Comunidades e Apoio aos Haitianos). O sistema oferece compreensão e geração de respostas em **qualquer idioma natural** pela IA, interface gráfica totalmente localizada em **5 idiomas oficiais** (Crioulo Haitiano, Francês, Inglês, Espanhol e Português), pipeline RAG de 3 passos com busca vetorial no PostgreSQL (`pgvector`), enforcement estrito de whitelist em buscas externas, aplicação rigorosa da **Regra de Ouro** (Zero Alucinação) e sessões anônimas efêmeras.

## Technical Context

**Language/Version**: Python 3.12+ com tipagem estática rigorosa (Type hints PEP 484).

**Primary Dependencies**: Django 5.x, Django REST Framework (DRF), LangChain, `pgvector`, `psycopg3`, `pytest-django`, `ruff`.

**Storage**: PostgreSQL 16+ com extensão `pgvector` unificando dados relacionais e armazenamento vetorial denso (1536 dimensões).

**Testing**: `pytest`, `pytest-django`, fixtures DRF e suíte de avaliação de Groundedness/RAG em `ia/evaluation/`.

**Target Platform**: Linux / Docker Container / PWA responsivo para Web e Mobile.

**Project Type**: Web Service + API REST (DRF) + Frontend Monolith com Django Templates & Vanilla CSS/JS.

**Performance Goals**: Tempo de resposta do chat < 5 segundos para o ciclo completo (detecção de idioma + busca vetorial/whitelist + geração do LLM).

**Constraints**: Tolerância ZERO a alucinações normativas (Groundedness = 100%); estrita aderência à Whitelist oficial de domínios; sessões anônimas sem armazenamento de PII.

**Scale/Scope**: 4 Pilares temáticos, 5 idiomas oficiais de interface, conversação aberta em qualquer língua, dezenas de fontes governamentais indexadas.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Absolute Groundedness & Zero-Hallucination Mandate**: O RAG utiliza o fluxo de 3 passos com a Regra de Ouro, sem dedução ou suposição jurídica.
- [x] **II. Strict Search Domain Whitelist Governance**: Ferramenta de busca web opera sob restrição forçada de domínios cadastrados em `apps.sources.WhitelistDomain`.
- [x] **III. Ephemeral Anonymous User Interaction**: Sessões isoladas por `session_id`, sem cadastro, sem login e sem upload de arquivos no MVP.
- [x] **IV. Multi-Engine & Multi-Provider Architecture**: Camada `ia/` totalmente desacoplada de `apps/` através de adaptadores e factory no LangChain.
- [x] **V. Defensive Security, Privacy & Input Sanitization**: Sanitização de inputs, prevenção contra prompt injection e isolamento total de segredos via `.env`.
- [x] **VI. Comprehensive Automated Testing & AI Evaluation Gates**: Testes automatizados com `pytest-django` e suíte de benchmarks anti-alucinação.
- [x] **VII. Production Observability & Traceability**: Logs estruturados em JSON e rastreabilidade de latência/tokens sem exposição de PII.

## Project Structure

### Documentation (this feature)

```text
specs/001-multilingual-migrant-chat/
├── spec.md              # Especificação de Requisitos e Histórias de Usuário
├── plan.md              # Este Plano de Implementação Técnica
├── research.md          # Fase 0: Decisões Arquiteturais e Pesquisas
├── data-model.md        # Fase 1: Modelagem Relacional e Vetorial
├── quickstart.md        # Fase 1: Guia de Execução e Validação Passo a Passo
├── checklists/
│   └── requirements.md  # Checklist de Qualidade da Especificação
└── contracts/
    └── chat-api.yaml    # Fase 1: Contrato OpenAPI 3.1 dos Endpoints REST
```

### Source Code (repository root)

```text
apps/
├── chat/                    # Gestão de Sessões Anônimas e Mensagens
│   ├── models.py            # AnonymousSession, ChatMessage
│   ├── serializers.py       # Serializers DRF para envio e histórico
│   ├── views.py             # Viewsets / APIViews do Chat
│   ├── urls.py              # Roteamento REST /api/v1/chat/
│   └── tests/               # Testes de integração e contrato DRF
├── knowledge/               # Base de Conhecimento Vetorial dos 4 Pilares
│   ├── models.py            # KnowledgeDocument, DocumentChunk (pgvector)
│   ├── services.py          # Serviço de busca por similaridade semântica
│   └── management/commands/ # Comando ingest_knowledge_base
├── sources/                 # Governança de Fontes Oficiais e ONGs
│   ├── models.py            # WhitelistDomain, OfficialSource, CommunityPartner
│   ├── serializers.py       # Serializers para parceiros e fontes
│   └── views.py             # Endpoint /api/v1/sources/partners/
ia/
├── embeddings/              # Serviços de geração de embeddings vetoriais
├── llm/                     # Factory de LLMs (OpenAI, Ollama, Anthropic)
├── prompts/                 # Prompts de sistema multilíngues e Regra de Ouro
├── rag/                     # Orquestração do RAG de 3 passos
├── retrieval/               # Vector retriever local + Search tool com Whitelist
└── evaluation/              # Testes automatizados de Groundedness e fidelidade
templates/                   # Layout PWA com seletor de 5 idiomas (Kreyòl, FR, EN, ES, PT)
static/
├── css/                     # Vanilla CSS estilizado e responsivo
└── js/                      # Lógica de chat assíncrono e catálogo de tradução i18n
```

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *Nenhuma violação identificada* | Arquitetura segue estritamente os padrões constitucionais do projeto | N/A |
