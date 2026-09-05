# MigrantIA 🌐🇧🇷

> **Assistente Inteligente de Orientação Jurídica, Documental e Apoio Comunitário a Migrantes no Brasil**

O **MigrantIA** é uma plataforma e assistente conversacional desenhado para orientar migrantes e refugiados (com foco especial na comunidade haitiana e demais populações vulneráveis) em processos de regularização migratória, emissão de documentos (RNM/CRNM, CPF, Carteira de Trabalho), direitos fundamentais, acesso à saúde/educação e redes de acolhimento no Brasil.

O projeto é guiado por uma **política de tolerância zero a alucinações**, garantindo que toda resposta seja rigorosamente fundamentada em leis oficiais, cartilhas governamentais e instituições de apoio verificadas.

---

## 📑 Sumário

- [Visão Geral e Princípios](#-visão-geral-e-princípios)
- [Fluxo de Resposta Anti-Alucinação](#-fluxo-de-resposta-anti-alucinação)
- [Diretrizes do MVP](#-diretrizes-do-mvp)
- [Arquitetura do Projeto](#-arquitetura-do-projeto)
- [Stack Tecnológica](#-stack-tecnológica)
- [Whitelist de Fontes Oficiais](#-whitelist-de-fontes-oficiais)
- [Instalação e Execução Local](#-instalação-e-execução-local)
- [Testes Automatizados](#-testes-automatizados)
- [Governança e Spec-Driven Development](#-governança-e-spec-driven-development)
- [Licença](#-licença)

---

## 🎯 Visão Geral e Princípios

- **Base Baseada em Evidências**: Informações jurídicas e procedimentais são extraídas de dados oficiais auditados.
- **Multilíngue por Design**: Suporte a múltiplos idiomas (Português, Crioulo Haitiano, Francês, Inglês, Espanhol, etc) para eliminar barreiras de acesso.
- **Privacidade e Proteção ao Migrante**: Coleta mínima de dados (*Data Minimization*), operando com sessões anônimas, sem login obrigatório e sem retenção de dados sensíveis (PII).
- **Transparência e Citação Ativa**: Todas as respostas confirmadas trazem o link direto para a fonte oficial consultada.

---

## 🛡️ Fluxo de Resposta Anti-Alucinação

Para garantir segurança jurídica e confiabilidade absoluta, o agente segue um **fluxo obrigatório de 3 passos**:

```mermaid
flowchart TD
    A[Pergunta do Usuário] --> B[Passo 1: Base Local - pgvector + Relacional]
    B -->|Encontrou informação precisa?| C[Responde com Citação da Fonte Local]
    B -->|Não encontrou ou requer tempo real| D[Passo 2: Busca Externa com Whitelist Estrita]
    D -->|Filtro site: nos domínios oficiais| E{Encontrou em fonte oficial?}
    E -->|Sim| F[Responde com Link Direto da Fonte Oficial]
    E -->|Não| G[Passo 3: Regra de Ouro / Não Sei]
    G --> H[Resposta Transparente Padronizada + Indicação de ONGs/Órgãos Oficiais]
```

1. **Passo 1 (Base Local)**: Consulta inicial ao banco vetorial `pgvector` (legislação, portarias, cartilhas, direitos básicos) e tabelas relacionais (diretório de ONGs, contatos jurídicos e centros de acolhimento).
2. **Passo 2 (Busca Externa na Whitelist)**: Caso a informação não conste na base local ou demande dados em tempo real (taxas atuais, agendamentos na PF, portarias recentes), o agente realiza busca web restrita **exclusivamente** aos domínios homologados (`site:`).
3. **Passo 3 (Regra de Ouro / "Não Sei" Transparente)**: Se a informação não for encontrada nos canais oficiais homologados, é **estritamente proibido** deduzir, chutar ou buscar em fontes abertas não verificadas. O agente responde com transparência:
   > *"Não encontrei essa informação nos canais oficiais consultados. Recomendo procurar diretamente uma das instituições de apoio cadastradas ou o órgão competente."*

---

## 🚀 Diretrizes do MVP

- **Backend em Python/Django**: Estruturado com Django REST Framework (DRF) e arquitetura modular monolith.
- **Banco de Dados com `pgvector`**: PostgreSQL 16+ unificando dados estruturados (ONGs, postos de atendimento) e dados vetoriais (embeddings de documentos legais).
- **Sessões Anônimas (`session_id`)**: Sessões temporárias isoladas via identificador anônimo, sem exigir cadastro/login e sem upload de arquivos no MVP.
- **Testes com `pytest-django`**: Testes unitários, de integração e avaliação contínua de groundedness do RAG.

---

## 🏛️ Arquitetura do Projeto

O repositório adota alta coesão e baixo acoplamento entre lógica de negócio (`apps/`) e infraestrutura de inteligência artificial (`ia/`):

```text
migrantIA/
├── apps/                    # Aplicações Django de Domínio de Negócio
│   ├── chat/                # Sessões anônimas, histórico de mensagens e APIs REST
│   ├── knowledge/           # Gestão de documentos, chunks e interface vetorial
│   └── sources/             # Registro de fontes oficiais, whitelist e diretório de ONGs
├── ia/                      # Módulo Desacoplado de IA e RAG
│   ├── embeddings/          # Serviços de geração de embeddings vetoriais
│   ├── evaluation/          # Datasets e avaliadores de fidelidade/precisão (anti-hallucination)
│   ├── ingestion/           # Loaders, cleaners, splitters e extração de metadados
│   ├── llm/                 # Factory e adaptadores para múltiplos provedores (OpenAI, Ollama, etc.)
│   ├── prompts/             # Prompts de sistema, templates RAG e suporte multilíngue
│   ├── rag/                 # Chains de orquestração e pipelines de resposta
│   └── retrieval/           # Retrievers locais (pgvector) e ferramenta de busca na Whitelist
├── config/                  # Configurações globais do Django (settings, urls, asgi/wsgi)
├── .specify/                # Especificações e Governança (Spec-Driven Development / SDD)
│   └── memory/              # Constituição e regras fundamentais do projeto
├── templates/               # Templates da interface PWA / Web
├── docker-compose.yml       # Orquestração de contêineres (Django + PostgreSQL/pgvector)
├── Dockerfile               # Build da aplicação
├── manage.py                # Utilitário de linha de comando Django
├── requirements.txt         # Dependências do projeto Python
└── README.md                # Documentação principal
```

---

## 💻 Stack Tecnológica

| Camada | Tecnologia | Descrição |
| :--- | :--- | :--- |
| **Linguagem** | Python 3.12+ | Tipagem estática e conformidade com PEP 8 (Ruff / Black) |
| **Backend** | Django 5.x / 6.x & DRF | API REST modular e serviços de domínio |
| **Banco de Dados** | PostgreSQL 16+ | Armazenamento relacional robusto |
| **Vector Store** | `pgvector` | Indexação e busca por similaridade semântica |
| **Orquestração de IA** | LangChain | Abstração de modelos, pipelines RAG e chains |
| **Testes** | `pytest` & `pytest-django` | Suíte de testes automatizados e quality gates |
| **Frontend/PWA** | Django Templates / PWA | Interface responsiva e acessível para dispositivos móveis |
| **Contêineres** | Docker & Docker Compose | Paridade entre ambientes de desenvolvimento e produção |

---

## 🌐 Whitelist de Fontes Oficiais

As consultas externas da IA são rigidamente filtradas através dos seguintes domínios confiáveis:

- **Governo Federal e Legislação**:
  - `gov.br` (Polícia Federal, Ministério da Justiça, MRE, MTE, etc.)
  - `planalto.gov.br` (Lei de Migração nº 13.445/2017, Decretos e Portarias)
- **Defensoria e Órgãos Judiciais**:
  - `dpu.def.br` (Defensoria Pública da União)
  - `defensoria.sp.def.br` e demais Defensorias Estaduais (`*.def.br`)
  - `cnj.jus.br` (Conselho Nacional de Justiça)
- **Organismos Internacionais e Comitês Nacionais**:
  - `acnur.org` / `help.unhcr.org` (ACNUR / UNHCR)
  - `iom.int` / `brazil.iom.int` (OIM - Organização Internacional para as Migrações)
  - `cniq.mj.gov.br` (CNIg - Conselho Nacional de Imigração)
  - `conare.mj.gov.br` (CONARE - Comitê Nacional para os Refugiados)
- **Organizações da Sociedade Civil e Universidades**:
  - `caritas.org.br` / `caritas.sp.org.br` (Cáritas Brasileira)
  - `missaopaz.org` (Missão Paz)
  - `refugio343.org`
  - `carolinabori.mec.gov.br` e domínios acadêmicos oficiais (`*.edu.br`)

---

## 🛠️ Instalação e Execução Local

### Pré-requisitos

- **Python 3.12+**
- **PostgreSQL 16+** com extensão `pgvector` (ou Docker instalado)
- **Git**

### Passo a Passo

1. **Clonar o repositório**:
   ```bash
   git clone https://github.com/seu-usuario/migrantIA.git
   cd migrantIA
   ```

2. **Criar e ativar o ambiente virtual**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # No Windows: .venv\Scripts\activate
   ```

3. **Instalar dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variáveis de ambiente**:
   Crie um arquivo `.env` na raiz do projeto:
   ```env
   DEBUG=True
   SECRET_KEY=sua-chave-secreta-de-desenvolvimento
   DATABASE_URL=postgres://postgres:postgres@localhost:5432/migrantia
   OPENAI_API_KEY=sua-chave-api-openai
   TAVILY_API_KEY=sua-chave-api-de-busca
   ```

5. **Executar migrações do banco de dados**:
   ```bash
   python manage.py migrate
   ```

6. **Iniciar o servidor de desenvolvimento**:
   ```bash
   python manage.py runserver
   ```
   Acesse a aplicação em `http://127.0.0.1:8000/`.

---

## 🧪 Testes Automatizados

O projeto utiliza `pytest` e `pytest-django` para validar serviços, endpoints REST, integridade vetorial e políticas anti-alucinação:

```bash
# Executar todos os testes
pytest

# Executar testes com relatório de cobertura
pytest --cov=apps --cov=ia

# Executar testes da suíte de avaliação RAG
pytest ia/evaluation/
```

---

## 📜 Governança e Spec-Driven Development

O **MigrantIA** segue a metodologia **Spec-Driven Development (SDD)** gerenciada pelo Spec Kit. Todas as decisões arquiteturais e operacionais são regidas pela **Constituição do Projeto** localizada em [`.specify/memory/constitution.md`](.specify/memory/constitution.md).

Qualquer alteração em princípios essenciais, novos fluxos de IA ou ferramentas de busca deve ser submetida e validada através de emendas constitucionais formais.

---
