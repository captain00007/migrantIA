# Feature Specification: APIs REST do Chat, Sessões Multilíngues e Governança LGPD

**Feature Branch**: `003-chat-api-sessions`  
**Created**: 2026-09-14  
**Status**: Completed ✅  

## 🎯 Objetivo
Implementar a camada de serviços web e APIs REST do **MigrantIA** (`apps/chat/`), permitindo que a aplicação frontend PWA crie sessões multilíngues, envie mensagens, receba respostas fundamentadas do pipeline RAG com fontes oficiais, registre feedback e garanta proteção integral de dados sensíveis (LGPD).

## 📋 Histórias de Usuário e Critérios de Aceite

### User Story 1 - Criação e Gestão de Sessões de Atendimento Multilíngue (P1)
Como um migrante ou refugiado acessando a plataforma pelo celular, quero iniciar uma sessão no meu idioma preferido (Kreyòl, Francês, Espanhol, Inglês ou Português) para que todas as minhas dúvidas sejam respondidas contextualmente nesse idioma.

**Critérios de Aceite:**
1. Endpoint `POST /api/chat/sessions/` cria uma nova sessão com UUID v4 e define o idioma `ui_language`.
2. A sessão armazena metadados de acesso de forma anônima e segura.
3. Sessões inativas podem ser recuperadas pelo seu `session_id` via `GET /api/chat/sessions/{id}/`.

### User Story 2 - Envio de Mensagens e Integração com RAG de 3 Passos (P1)
Como um usuário com dúvidas sobre documentação ou educação, quero enviar minha pergunta e receber uma resposta oficial acompanhada das fontes governamentais citadas e aviso claro caso a Regra de Ouro tenha sido aplicada.

**Critérios de Aceite:**
1. Endpoint `POST /api/chat/sessions/{id}/messages/` recebe a pergunta e aciona o `ChatService` integrado ao `RAGPipeline`.
2. A resposta inclui o texto formatado, array de fontes (`sources_cited`), idioma detectado e flag `golden_rule_triggered`.
3. O histórico recente da conversa é repassado como memória para o pipeline.

### User Story 3 - Proteção de Privacidade e Anonimização LGPD (P1)
Como uma pessoa vulnerável, quero garantia absoluta de que meus dados pessoais sensíveis (CPF, Passaporte, RNM, telefone, e-mail) não serão expostos ou gravados em texto claro no banco de dados.

**Critérios de Aceite:**
1. Módulo `apps/chat/privacy.py` detecta e mascara dados sensíveis antes de salvar no banco e antes de enviar ao LLM.
2. Nenhuma chave de identificação direta do migrante é persistida sem anonimização.

### User Story 4 - Feedback e Avaliação de Respostas (P2)
Como um usuário ou mediador comunitário, quero avaliar se a resposta foi útil (👍 ou 👎) e indicar o motivo caso haja imprecisão, para que a curadoria oficial possa auditar a base de conhecimento.

**Critérios de Aceite:**
1. Endpoint `POST /api/chat/messages/{id}/feedback/` registra o rating (`+1` ou `-1`), categoria do motivo e comentário opcional.
2. Cada mensagem pode receber apenas um feedback por sessão.
