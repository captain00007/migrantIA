# Quickstart & Validation Guide: Chat Multilíngue (Quatro Pilares)

**Feature**: `001-multilingual-migrant-chat` | **Date**: 2026-09-05

## 1. Pré-requisitos & Ambiente

- **Python 3.12+** e ambiente virtual ativo
- **PostgreSQL 16+** com extensão `pgvector` instalada (ou via Docker Compose)
- Dependências instaladas: `pip install -r requirements.txt`

## 2. Configuração de Variáveis de Ambiente

Crie ou atualize o arquivo `.env` na raiz do projeto:

```env
DEBUG=True
SECRET_KEY=dev-secret-key-migrantia-2026
DATABASE_URL=postgres://postgres:postgres@localhost:5432/migrantia
OPENAI_API_KEY=sua-chave-api-openai
TAVILY_API_KEY=sua-chave-api-de-busca
```

## 3. Inicialização e Carga da Base de Conhecimento

Execute as migrações do banco e carregue a semente de dados dos 4 pilares:

```bash
# Executar migrações do banco de dados (tabelas relacionais + pgvector)
python manage.py migrate

# Popular domínios homologados na Whitelist e Diretório de Parceiros
python manage.py loaddata apps/sources/fixtures/initial_whitelist.json
python manage.py loaddata apps/sources/fixtures/initial_partners.json

# Ingerir e indexar a base inicial de conhecimento dos Quatro Pilares
python manage.py ingest_knowledge_base
```

## 4. Execução dos Testes Automatizados

Valide todos os contratos de API, serviços de RAG e qualidade anti-alucinação:

```bash
# Testes unitários e de integração Django REST Framework
pytest

# Testes de avaliação do RAG nos 4 pilares e suporte multilíngue
pytest ia/evaluation/ -v
```

## 5. Cenários de Validação Manual dos 4 Pilares

Inicie o servidor de desenvolvimento:
```bash
python manage.py runserver
```
Acesse `http://localhost:8000/` e execute os seguintes testes:

| Cenário de Teste | Idioma | Pergunta de Entrada | Resultado Esperado |
| :--- | :--- | :--- | :--- |
| **Pilar 1 (Imigração)** | Crioulo Haitiano | *"Kouman mwen ka jwenn CPF mwen an Brezil?"* | Resposta em Crioulo com instruções oficiais e link para Receita Federal/Correios. |
| **Pilar 2 (Educação)** | Francês | *"Comment fonctionne la validation de diplôme sur Carolina Bori?"* | Resposta em Francês com explicação da Plataforma Carolina Bori e link do MEC. |
| **Pilar 3 (Nacionalidade)** | Português | *"Quais os requisitos para naturalização ordinária?"* | Resposta com prazos da Lei 13.445/17, comprovantes aceitos (Celpe-Bras) e link do MJ. |
| **Pilar 4 (Apoio Haitiano)** | Crioulo Haitiano | *"Mwen bezwen asistans legal gratis pou lapolis federal."* | Resposta com contato oficial da Defensoria Pública da União (DPU) e instituições parceiras. |
| **Regra de Ouro (Não Sei)** | Espanhol | *"¿Existe una amnistía secreta para multas de migrantes este mes?"* | Resposta transparente declarando que a informação não consta em fontes oficiais e indicando a DPU. |
| **Seletor de Idioma da UI** | N/A | Alternar entre 🇭🇹 Kreyòl, 🇫🇷 Français, 🇺🇸 English, 🇪🇸 Español, 🇧🇷 Português | 100% dos textos da interface atualizados instantaneamente no idioma escolhido. |
