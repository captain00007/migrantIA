# Phase 0 Research: Chat de Orientação e Consulta Multilíngue para Migrantes (Quatro Pilares)

**Feature**: `001-multilingual-migrant-chat` | **Date**: 2026-09-05

## Research Summary & Technical Decisions

### 1. Multilingual AI Engine & Prompt Orchestration
- **Decision**: Utilizar prompts de sistema especializados no LangChain que instruem o LLM a espelhar dinamicamente o idioma da mensagem do usuário (Crioulo Haitiano, Francês, Espanhol, Inglês, Português ou qualquer outro), mantendo a interpretação fidedigna das fontes normativas brasileiras (que estão originalmente em Português).
- **Rationale**: Usuários em situação de refúgio ou migração se comunicam prioritariamente em seu idioma materno. O motor de IA traduz o significado semântico para a busca vetorial e gera a resposta explicativa no idioma do usuário, com vocabulário simples e empático.
- **Alternatives Considered**:
  - *Tradutor intermediário pré e pós-LLM*: Rejeitado por adicionar latência excessiva (>3s adicionais) e risco de perder nuances jurídicas em traduções duplas.
  - *Modelos separados por idioma*: Rejeitado por complexidade desnecessária de infraestrutura e custos operacionais.

### 2. Internacionalização da Interface (5 Idiomas Oficiais)
- **Decision**: Implementar catálogo de internacionalização bilíngue/multilíngue estruturado em JSON para o frontend PWA (`locales/{lang}.json` cobrindo `ht`, `fr`, `en`, `es`, `pt`) integrado ao suporte nativo de i18n do Django.
- **Rationale**: Garante troca instantânea de idioma no cliente sem recarregamento de página, garantindo que botões, avisos institucionais e alertas da Regra de Ouro sejam 100% legíveis.
- **Alternatives Considered**:
  - *Google Translate Widget*: Rejeitado por falta de controle de precisão e péssima qualidade de tradução para Crioulo Haitiano (*Kreyòl*).

### 3. Pipeline RAG de 3 Passos & Enforcement de Whitelist
- **Decision**: Arquitetura sequencial em 3 etapas com barreiras estritas:
  1. **Passo 1 (Local)**: Consulta ao PostgreSQL com `pgvector` usando busca por cosseno (`<=>`) nos chunks dos 4 pilares + diretório relacional de parceiros.
  2. **Passo 2 (Busca Externa na Whitelist)**: Se o score local for insuficiente (< 0.75) ou a pergunta exigir dados em tempo real, executa busca via adaptador com restrição forçada de `site:gov.br OR site:planalto.gov.br OR site:dpu.def.br OR site:acnur.org ...`.
  3. **Passo 3 (Regra de Ouro / Não Sei Transparente)**: Se a informação oficial não for encontrada, o pipeline intercepta a geração e retorna a mensagem padronizada no idioma do usuário, indicando os contatos da DPU e ONGs parceiras.
- **Rationale**: Cumpre rigorosamente a Seção I e V da Constituição do MigrantIA (Zero Alucinação e Governança de Fontes Oficiais).
- **Alternatives Considered**:
  - *Busca web aberta sem restrição de domínio*: Rejeitado categoricamente pela Constituição.

### 4. Gestão de Sessões Anônimas e Efêmeras
- **Decision**: Sessões anônimas isoladas via `session_id` (UUIDv4) trafegadas via header `X-Session-ID` ou cookie seguro, armazenando histórico temporário no PostgreSQL com expiração automática (TTL configurável).
- **Rationale**: Atende à exigência constitucional de proteção de dados de populações vulneráveis, dispensando autenticação, senhas ou armazenamento de PII no MVP.
- **Alternatives Considered**:
  - *Sessões puramente in-memory (sem banco)*: Rejeitado porque impede perguntas de acompanhamento em caso de reconexão mobile.

### 5. PostgreSQL + pgvector como Vector Store Unificado
- **Decision**: Utilizar PostgreSQL 16 com extensão `pgvector` via `pgvector-python` e campos de vetor no Django ORM.
- **Rationale**: Elimina a necessidade de gerenciar um banco vetorial externo separado (ex: Pinecone, Qdrant), reduzindo a complexidade de deploy para um único serviço de banco de dados no `docker-compose.yml`.
