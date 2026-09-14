# Feature Specification: Motor de IA, Prompts Multilíngues e Pipeline RAG de Três Passos

**Feature Branch**: `002-ai-engine-rag-pipeline`  
**Created**: 2026-09-14  
**Status**: Completed ✅  

## 🎯 Objetivo
Implementar o motor de Inteligência Artificial do **MigrantIA**, composto pela fábrica multi-provedor de LLMs (`ia/llm/`), templates de prompts multilíngues com salvaguarda da Regra de Ouro (`ia/prompts/`), ferramenta de busca externa restrita à whitelist oficial de domínios (`ia/retrieval/`) e o orquestrador do **Fluxo RAG de 3 Passos** (`ia/rag/`).

## 📋 Histórias de Usuário e Critérios de Aceite

### User Story 1 - Resposta Fundamentada a partir da Base Vetorial Local (P1)
Como um migrante consultando sobre regularização ou refúgio, quero que minha pergunta seja respondida com base em leis e cartilhas oficiais indexadas no `pgvector`, no meu idioma, com citação expressa da fonte e do artigo/norma aplicável.

**Critérios de Aceite:**
1. A pergunta é analisada e o retriever semântico/híbrido localiza os trechos relevantes no `pgvector`.
2. O LLM gera a resposta respondendo no mesmo idioma do usuário com links oficiais e referências normativas.
3. Não havendo necessidade de busca web, a resposta é entregue com alto desempenho e fundamentação.

### User Story 2 - Consulta de Dados Recentes via Busca na Whitelist Estrita (P1)
Como um solicitante que pergunta sobre taxas atuais ou procedimentos recentes no banco local, quero que o sistema busque em tempo real exclusivamente nos domínios governamentais e de ONGs homologadas (`gov.br`, `dpu.def.br`, `acnur.org`, etc).

**Critérios de Aceite:**
1. Quando a base local não contiver a resposta suficiente, o orquestrador aciona a busca externa.
2. A consulta web é forçada a conter apenas domínios de `WhitelistDomain` (`include_domains`).
3. Fontes externas fora da whitelist são rigorosamente descartadas.

### User Story 3 - Aplicação Rigorosa da Regra de Ouro / Zero Alucinação (P1)
Como uma pessoa vulnerável, quero ter certeza absoluta de que o assistente não inventará dados jurídicos ou prazos caso a informação oficial não exista.

**Critérios de Aceite:**
1. Quando nem a base local nem a busca na whitelist fornecerem evidência oficial confirmada, o agente aciona a Regra de Ouro.
2. A resposta é transparente e padronizada no idioma do usuário, recomendando procurar os órgãos competentes ou as instituições cadastradas (`CommunityPartner`).
3. Groundedness = 100% zero tolerância a suposições ou deduções.

## 🏛️ Arquitetura de Componentes
1. **`ia/llm/`**: `LLMFactory` suportando OpenAI, Google Gemini e Ollama local.
2. **`ia/prompts/`**: System prompts multidiomas, suporte aos 5 idiomas (Kreyòl, FR, ES, EN, PT) e template da Regra de Ouro.
3. **`ia/retrieval/search.py`**: Ferramenta de busca externa com filtro estrito de domínios de `apps.sources.WhitelistDomain`.
4. **`ia/rag/`**: `RAGPipeline` e `RAGChain` executando o fluxo de 3 passos e formatando o objeto `RAGResponse`.
