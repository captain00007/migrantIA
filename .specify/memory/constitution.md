<!--
Sync Impact Report:
- Version change: 1.0.0 -> 1.1.0
- Ratification: 2026-09-04 | Amended: 2026-09-05
- Principles defined / amended:
  1. I. Modular Monolith Architecture & Simplicity
  2. II. Zero-Hallucination Policy & Mandatory 3-Step Agent Response Workflow (Expanded)
  3. III. Search Tool Whitelisting & Direct Official Source Citation (Added / Expanded)
  4. IV. Dual-Data Modeling: Relational vs. Vector (pgvector)
  5. V. Anonymous Session Isolation, Data Minimization & Migrant Privacy (MVP Directives Defined)
  6. VI. Comprehensive Automated Testing (pytest-django) & AI Evaluation Gates (Testing Stack Updated)
  7. VII. Production Observability & Traceability
- Added / Updated sections:
  - Agent Response Protocol & Search Whitelist Policy (Steps 1, 2, 3 + Golden Rule)
  - Strict Domain Whitelist Specification with mandatory `site:` enforcement
  - MVP Architectural Directives (Django + PostgreSQL + pgvector, anonymous session_id, no login/file uploads, pytest-django)
- Removed sections: None
- Follow-up TODOs: None
-->

# MigrantIA Constitution

## Core Principles

### I. Modular Monolith Architecture & Simplicity
- The system MUST be structured as a modular monolith within a single cohesive repository.
- Unnecessary distributed-system complexity (such as premature microservices, asynchronous message brokers, or multi-repo fragmentation) is strictly prohibited.
- Modules MUST maintain high cohesion and loose coupling:
  - Business domain apps reside under `apps/` (e.g., `knowledge`, `sources`, `chat`, Haitian community modules).
  - Framework-agnostic AI and RAG infrastructure reside under `ia/` (ingestion, embeddings, retrieval, chains, prompts, evaluation, provider adapters).
  - Global routing and project settings reside under `config/`.

### II. Zero-Hallucination Policy & Mandatory 3-Step Agent Response Workflow
- Hallucinations, ungrounded factual claims, speculative legal advice, and unverified procedural guidance are classified as **Critical System Defects** and security violations.
- All AI-generated guidance MUST strictly adhere to the **Mandatory 3-Step Response Workflow**:
  1. **Passo 1 (Base Local - Vector Store & Relational Directory)**:
     - The agent MUST first query the internal PostgreSQL `pgvector` knowledge base (official laws, normative resolutions, basic rights, official guidebooks) and relational database (verified NGO directory, support centers, legal contacts).
  2. **Passo 2 (Busca na Internet com Whitelist Estrita)**:
     - If the required information is NOT present in the local database, or if the user query demands real-time data (e.g., current administrative fees, recent ministerial decrees, appointment availability/schedules), the agent MUST perform a web search **EXCLUSIVELY** within the pre-approved domain whitelist using strict `site:` operators.
  3. **Passo 3 (Regra de Ouro / Resposta de Não-Saber com Transparência)**:
     - If the information is NOT found in either the local base or the official whitelisted domains, the agent is **STRICTLY FORBIDDEN** from querying unverified open-web sources, guessing, inferring, or fabricating answers.
     - The agent MUST respond transparently with the standardized refusal/fallback message:
       > *"Não encontrei essa informação nos canais oficiais consultados. Recomendo procurar diretamente uma das instituições de apoio cadastradas ou o órgão competente."*
- Model provider abstraction MUST be preserved via LangChain and adapter interfaces; switching LLM or embedding providers MUST NOT alter core domain retrieval or business logic.

### III. Search Tool Whitelisting & Direct Official Source Citation
- **Strict Domain Whitelist**: Web search capabilities MUST be strictly gated. Every outbound query MUST enforce domain filtering (e.g., `site:<domain>`).
- The authorized Whitelist comprises exclusively official government, multilateral, legal defense, and certified support organizations:
  - **Governo Federal e Legislação Brasileira**: `gov.br` (Polícia Federal, Ministério da Justiça, MRE, MTE, etc.), `planalto.gov.br` (Lei nº 13.445/2017, Decretos e Portarias).
  - **Defensoria e Órgãos de Justiça**: `dpu.def.br`, `defensoria.sp.def.br` e demais Defensorias Públicas Estaduais (`*.def.br`), `cnj.jus.br`.
  - **Organismos Internacionais e Comitês Nacionais**: `acnur.org` / `help.unhcr.org` (ACNUR/UNHCR), `iom.int` / `brazil.iom.int` (OIM), `cniq.mj.gov.br` (CNIg), `conare.mj.gov.br` (CONARE).
  - **Redes de Apoio e Educação Verificadas**: `caritas.org.br`, `caritas.sp.org.br`, `missaopaz.org`, `refugio343.org`, portais acadêmicos oficiais para validação de diplomas (`carolinabori.mec.gov.br`, `*.edu.br`).
- Any search request attempting to query domains outside this whitelist MUST be rejected immediately by the search tool.
- **Mandatory Direct Link Citation**: Every confirmed response provided to the migrant MUST conclude with a direct Markdown citation link to the official consulted source (e.g., `[Polícia Federal - Regularização Migratória](https://www.gov.br/pf/...)`).
- Answers generated without verifiable backing from these authorized sources constitute a critical safety and compliance failure.

### IV. Dual-Data Modeling: Relational vs. Vector
- Data MUST be cleanly segregated between structured relational models and unstructured semantic embeddings:
  - **Structured Domain Entities**: Community organizations, support centers, legal contacts, and administrative bodies MUST be stored in relational PostgreSQL tables with strict schema constraints, indexing, and foreign keys.
  - **Unstructured Knowledge**: Regulatory texts, immigration guides, step-by-step procedures, and educational opportunities MUST be chunked, embedded, and stored in PostgreSQL using the `pgvector` extension.
  - **Hybrid Querying**: Where queries require both category/entity scoping and semantic search, hybrid relational SQL filtering and vector similarity search MUST be used.

### V. Anonymous Session Isolation, Data Minimization & Migrant Privacy
- **Anonymous Sessions for MVP**: To ensure immediate accessibility and zero friction for vulnerable migrants, interactions operate under stateless, isolated sessions identified via an anonymous `session_id`.
- **No Login / No File Uploads in MVP**: The MVP scope strictly prohibits user login requirements and file/document uploads. No migrant credentials, passwords, or personal documents are accepted or stored.
- **Data Minimization & Zero PII Leakage**: No personally identifiable information (PII) or sensitive query content may be stored in permanent prompt logs, third-party telemetry, or unencrypted storage.
- Standard defensive security (OWASP Top 10) MUST be enforced across all endpoints: parameterized queries, robust input sanitization, rate limiting, and 12-factor configuration (zero hardcoded secrets).

### VI. Comprehensive Automated Testing & AI Evaluation Gates
- Automated testing is non-negotiable across all code layers:
  - **pytest-django**: All Django backend tests (models, views, services, API contracts) MUST be implemented using `pytest` with the `pytest-django` plugin.
  - **API Contract Tests**: Django REST Framework (DRF) endpoints MUST have integration tests verifying input validation, error handling, status codes, and JSON response structures.
  - **AI/RAG Evaluation Benchmarks**: Evaluation suites MUST benchmark retrieval precision/recall, context relevance, faithfulness (groundedness), and hallucination detection before merging changes.
- CI/CD pipelines MUST execute linters (Ruff/Black), type checks (mypy/pyright), `pytest-django` suites, and RAG evaluation benchmarks as blocking merge gates.

### VII. Production Observability & Traceability
- All critical workflows and REST API endpoints MUST produce structured JSON logs and operational telemetry.
- AI/RAG operations MUST incorporate end-to-end tracing capturing prompt versions, retrieval latencies, embedding generation durations, token consumption, model identifiers, and error rates without exposing user PII.

## Technology Standards & Architecture

### Stack Specifications
- **Runtime & Language**: Python 3.12+ with explicit type annotations throughout the codebase.
- **Backend Framework**: Django 5.x with Django REST Framework (DRF) for REST APIs.
- **Test Framework**: `pytest` and `pytest-django` for unit, integration, and API contract testing.
- **Frontend / Client**: Monolith architecture serving a responsive Progressive Web App (PWA) client interface.
- **Database & Vector Store**: PostgreSQL 16+ with the `pgvector` extension for unified relational and vector storage.
- **AI & RAG Orchestration**: LangChain integrated through custom abstraction layers ensuring model/provider neutrality.
- **Web Search Engine**: Search provider adapter with mandatory whitelist filtering (`site:` operator restriction).
- **Session Architecture**: Ephemeral anonymous sessions isolated via `session_id` (cookie/header); no user authentication or file uploads in MVP.
- **Containerization**: Docker with multi-stage `Dockerfile` and `docker-compose.yml` for local development and production environment parity.
- **CI/CD**: Automated GitHub Actions pipelines for formatting, linting, testing, security audits, and evaluation checks.

### Architectural Boundaries
- `apps/`: Domain-specific Django applications:
  - `apps/knowledge/`: Unstructured knowledge management, document chunk models, vector search interface.
  - `apps/sources/`: Official sources registry, whitelist management, and verified community directory.
  - `apps/chat/`: Anonymous session management, chat history, and DRF conversation endpoints.
- `ia/`: Framework-agnostic AI and RAG engine:
  - `ia/ingestion/`: Document loaders, cleaners, splitters, and metadata extractors.
  - `ia/embeddings/`: Embedding service and vector representations.
  - `ia/retrieval/`: Local vector retriever, hybrid filters, and search tool with whitelist enforcers.
  - `ia/rag/`: Orchestration pipeline, chains, and grounded response formatters.
  - `ia/llm/`: Multi-provider adapters and factory.
  - `ia/prompts/`: Multilingual system prompts and fallback templates.
  - `ia/evaluation/`: Datasets, ground-truth benchmarks, and faithfulness evaluators.
- `config/`: Application settings, environment configuration, WSGI/ASGI entrypoints, and global routing.

## Coding & Engineering Conventions

### Python & Django Standards
- **Style Guide**: Code MUST conform to PEP 8 standards, enforced via automated tooling (Ruff / Black).
- **Type Safety**: Type hints MUST be applied to all public function signatures, method arguments, and service boundaries.
- **Service Layer Pattern**: Business logic, RAG retrieval orchestration, and data transformations MUST reside in dedicated domain services/managers rather than inside view controllers or serializers.
- **API Contracts**: All REST API endpoints MUST use DRF Serializers with explicit field definitions and strict input validation.

### Documentation Standards
- Every module, class, and public function MUST include docstrings explaining its purpose, parameters, return values, and exceptions.
- RAG prompt templates, chunking strategies, domain whitelist rules, and retrieval architectures MUST be documented in Markdown within the repository.

## Testing & Quality Standards

### Automated Testing Tiers
1. **Unit Tests (`pytest-django`)**: Fast, isolated tests for pure functions, data parsers, custom serializers, and isolated services (with mocked external AI and search providers).
2. **Integration Tests (`pytest-django`)**: Tests verifying Django ORM operations, database migrations, DRF endpoint responses, and `pgvector` similarity queries against a test PostgreSQL instance.
3. **AI/RAG Evaluation Suite**: Benchmark datasets assessing retrieval precision/recall and answer groundedness/faithfulness against the official whitelist.

### Quality Gates
- All pull requests MUST pass linting, type checks, unit tests, and integration tests before merging.
- Any regression in test coverage or RAG evaluation metrics (especially groundedness / zero-hallucination thresholds) MUST block deployment.

## Security, Privacy & Search Governance

- **Search Whitelist Enforcement**: All external search tools MUST programmatically validate queries against the allowed whitelist. Requests to bypass or broaden search domains MUST raise a security exception.
- **Credential Isolation**: Secrets, API tokens (LLM providers, search APIs), and database credentials MUST NEVER be committed to Git; they MUST be injected via environment variables (`.env` for local development, secrets manager in CI/production).
- **Input Validation**: All incoming requests and AI prompts MUST undergo strict validation and sanitization to prevent prompt injection and adversarial manipulation.
- **Data Protection**: User interactions MUST remain strictly anonymous in the MVP; telemetry MUST mask or redact any accidental PII.

## Spec-Driven Development (SDD) & Governance

### Spec Kit Lifecycle
- All non-trivial feature development MUST strictly follow the Spec-Driven Development (SDD) lifecycle:
  1. **Specification** (`.specify/` specs): Clarify objectives, requirements, constraints, and acceptance criteria.
  2. **Plan**: Architecture design, domain contracts, and technical approach.
  3. **Tasks**: Breakdown into actionable, testable implementation tasks.
  4. **Implementation**: Test-driven execution of tasks with constitutional validation.
- Application code MUST NOT be written or refactored without an approved spec and task plan.

### Constitutional Authority & Amendment Policy
- This Constitution supersedes all informal or ad-hoc project decisions.
- Any modification to core principles, architectural boundaries, or governance requires a formal constitutional amendment:
  - **MAJOR (x.0.0)**: Incompatible changes, removal/redefinition of core principles or architecture.
  - **MINOR (1.x.0)**: Addition of new principles, quality gates, search policies, or technology standards.
  - **PATCH (1.0.x)**: Clarifications, wording improvements, non-semantic refinements.
- All code reviews and PR evaluations MUST verify compliance with this Constitution.

## Git & Change Management

- **Branching**: Short-lived feature branches originating from `main` (`feat/`, `fix/`, `docs/`, `spec/`).
- **Commit Messages**: Enforce Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`, `ci:`).
- **Pull Requests**: Require clean CI runs, passing test/eval suites, and explicit alignment with Spec Kit tasks.

**Version**: 1.1.0 | **Ratified**: 2026-09-04 | **Last Amended**: 2026-09-05
