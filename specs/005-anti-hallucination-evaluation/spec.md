# Feature Specification: Avaliação Anti-Alucinação, Métricas RAG e Homologação Constitucional

**Feature Branch**: `005-anti-hallucination-evaluation`  
**Created**: 2026-09-14  
**Status**: Completed ✅  

## 🎯 Objetivo
Implementar o arcabouço formal de avaliação contínua, auditoria e homologação de qualidade anti-alucinação do **MigrantIA** (`ia/evaluation/`), assegurando que o motor RAG opere com 100% de fundamentação e que o acionamento da Regra de Ouro seja rigorosamente cumprido em todos os 5 idiomas e 4 pilares temáticos.

## 📋 Histórias de Usuário e Critérios de Aceite

### User Story 1 - Benchmark Multilíngue de Homologação (P1)
Como comitê de governança do MigrantIA, quero rodar um dataset de perguntas reais e perguntas-armadilha para auditar se o sistema responde com precisão quando há dados oficiais e aciona a Regra de Ouro quando não há evidências.

**Critérios de Aceite:**
1. O dataset cobre os 4 pilares e os 5 idiomas (`ht`, `fr`, `es`, `en`, `pt`).
2. Casos sem evidência validada oficial disparam a Regra de Ouro com segurança contra desinformação.

### User Story 2 - Métricas Estruturadas de Groundedness e Alucinação (P1)
Como engenheiro de IA, quero métricas quantitativas de fidelidade ao contexto (Groundedness), relevância e penalização por alucinações para validar novos modelos ou alterações de prompts.

**Critérios de Aceite:**
1. Funções de métricas calculam precisão da Regra de Ouro, cobertura de palavras-chave oficiais e penalidade de termos proibidos.
2. Relatório de homologação indica categoricamente aprovação ou reprovação com métricas detalhadas.

### User Story 3 - Comando de Homologação CLI (P2)
Como operador de DevOps/CI-CD, quero executar a homologação via comando de terminal `python manage.py evaluate_rag` para impedir deploys de modelos com desvios éticos.

**Critérios de Aceite:**
1. O comando executa os casos de teste do benchmark e imprime uma tabela formatada de desempenho.
2. Exportação opcional para arquivo JSON para dashboards de auditoria.
