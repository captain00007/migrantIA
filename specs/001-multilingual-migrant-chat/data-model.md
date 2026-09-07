# Data Model: Chat de Orientação e Consulta Multilíngue (Quatro Pilares)

**Feature**: `001-multilingual-migrant-chat` | **Date**: 2026-09-05

## Diagrama Entidade-Relacionamento

```mermaid
erDiagram
    AnonymousSession ||--o{ ChatMessage : "possui"
    OfficialSource }|--|| WhitelistDomain : "pertence a"
    KnowledgeDocument ||--o{ DocumentChunk : "dividido em"
    OfficialSource ||--o{ KnowledgeDocument : "origina"
    KnowledgeDocument }o--|| KnowledgePillar : "classificado em"
    CommunityPartner }o--|| KnowledgePillar : "atua em"

    AnonymousSession {
        uuid id PK
        string ui_language "ht, fr, en, es, pt"
        timestamp created_at
        timestamp last_activity
        json metadata
    }

    ChatMessage {
        uuid id PK
        uuid session_id FK
        string role "user, assistant, system"
        text content
        string language_detected
        boolean golden_rule_triggered
        json cited_sources
        timestamp created_at
    }

    WhitelistDomain {
        int id PK
        string domain UK "gov.br, dpu.def.br, acnur.org..."
        string organization_name
        boolean is_active
        timestamp created_at
    }

    OfficialSource {
        int id PK
        int domain_id FK
        string name
        string url
        string pillar "IMMIGRATION, EDUCATION, NATIONALITY, COMMUNITY"
        string authority_level
        timestamp created_at
    }

    KnowledgeDocument {
        int id PK
        int source_id FK
        string title
        string pillar
        string document_type "LAW, DECREE, ORDINANCE, GUIDE, FAQ"
        string url
        string hash
        timestamp updated_at
    }

    DocumentChunk {
        int id PK
        int document_id FK
        text content
        vector embedding "1536 dimensions"
        int chunk_index
        json metadata
    }

    CommunityPartner {
        int id PK
        string name
        string partner_type "LEGAL, RECEPTION, EDUCATIONAL, COMMUNITY"
        string city
        string state
        string phone
        string email
        string website
        json languages_supported "['ht', 'fr', 'pt', 'en', 'es']"
        text services_description
        boolean is_verified
    }
```

## Descrição das Entidades

### 1. `AnonymousSession` (`apps/chat/models.py`)
- **Propósito**: Representa a sessão de interação temporária do usuário migrante.
- **Campos**:
  - `id` (UUIDField, primary_key): Identificador único da sessão gerado pelo cliente ou backend.
  - `ui_language` (CharField, max_length=10, default='pt'): Idioma atual selecionado para a interface (`ht`, `fr`, `en`, `es`, `pt`).
  - `created_at` (DateTimeField, auto_now_add=True): Data/hora de início da sessão.
  - `last_activity` (DateTimeField, auto_now=True): Timestamp da última mensagem para cálculo de expiração.

### 2. `ChatMessage` (`apps/chat/models.py`)
- **Propósito**: Armazena as mensagens individuais da conversa (perguntas e respostas).
- **Campos**:
  - `id` (UUIDField, primary_key): Identificador da mensagem.
  - `session` (ForeignKey -> `AnonymousSession`, on_delete=CASCADE): Sessão vinculada.
  - `role` (CharField): Papel do emissor (`user`, `assistant`, `system`).
  - `content` (TextField): Conteúdo em texto da mensagem.
  - `language_detected` (CharField, max_length=10): Código do idioma detectado na mensagem.
  - `golden_rule_triggered` (BooleanField, default=False): Indica se a Regra de Ouro foi acionada.
  - `cited_sources` (JSONField, default=list): Lista de fontes oficiais com título, URL e trecho de referência.
  - `created_at` (DateTimeField, auto_now_add=True): Timestamp da mensagem.

### 3. `WhitelistDomain` & `OfficialSource` (`apps/sources/models.py`)
- **Propósito**: Governança e autorização de domínios para busca externa e curadoria de fontes.
- **Campos `WhitelistDomain`**:
  - `id` (AutoField, primary_key)
  - `domain` (CharField, unique=True): Domínio homologado (ex: `gov.br`, `planalto.gov.br`, `dpu.def.br`, `acnur.org`).
  - `organization_name` (CharField): Nome do órgão/instituição.
  - `is_active` (BooleanField, default=True): Status de liberação.

### 4. `KnowledgeDocument` & `DocumentChunk` (`apps/knowledge/models.py`)
- **Propósito**: Armazenamento e indexação semântica das leis, portarias e cartilhas dos 4 pilares.
- **Campos `DocumentChunk`**:
  - `id` (AutoField, primary_key)
  - `document` (ForeignKey -> `KnowledgeDocument`, on_delete=CASCADE)
  - `content` (TextField): Texto do fragmento (chunk).
  - `embedding` (VectorField, dimensions=1536): Vetor denso gerado pelo modelo de embeddings.
  - `chunk_index` (IntegerField): Posição ordinal no documento.
  - `metadata` (JSONField): Dados de contexto (título, artigo, pilar, fonte).

### 5. `CommunityPartner` (`apps/sources/models.py`)
- **Propósito**: Diretório estruturado de acolhimento e assistência jurídica gratuita aos migrantes.
- **Campos**:
  - `name` (CharField): Nome da organização (ex: Defensoria Pública da União, Cáritas, Missão Paz).
  - `partner_type` (CharField): `LEGAL`, `RECEPTION`, `EDUCATIONAL`, `COMMUNITY`.
  - `city`, `state` (CharField): Localização do atendimento.
  - `phone`, `email`, `website` (CharField/URLField): Informações de contato direto.
  - `languages_supported` (JSONField): Lista de idiomas atendidos (`['ht', 'fr', 'pt', 'en', 'es']`).
  - `services_description` (TextField): Descrição dos serviços prestados.
  - `is_verified` (BooleanField, default=True): Validação de autenticidade da entidade.
