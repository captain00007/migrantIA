# Feature Specification: Interface Frontend PWA Multilíngue e Acessível

**Feature Branch**: `004-multilingual-pwa-interface`  
**Created**: 2026-09-14  
**Status**: Completed ✅  

## 🎯 Objetivo
Construir a interface do usuário (Frontend PWA Mobile-First) do **MigrantIA**, proporcionando uma experiência acolhedora, rápida, acessível e multilíngue (Kreyòl, Francês, Espanhol, Inglês, Português), com síntese/reconhecimento de voz, filtro dos 4 pilares temáticos, cards de fontes oficiais verificadas e suporte offline.

## 📋 Histórias de Usuário e Critérios de Aceite

### User Story 1 - Acesso Instantâneo em 5 Idiomas (P1)
Como um migrante recém-chegado ao Brasil que fala apenas Crioulo Haitiano ou Francês, quero abrir o aplicativo e selecionar meu idioma com um clique no topo da tela, para que todos os botões, mensagens e respostas apareçam no meu idioma nativo.

**Critérios de Aceite:**
1. O seletor de idiomas no topo permite alternar entre `ht`, `fr`, `es`, `en` e `pt` sem recarregar a página.
2. O idioma ativo é persistido no `localStorage` e repassado para a sessão do backend.

### User Story 2 - Consulta por Voz e Leitura em Áudio / Acessibilidade (P1)
Como uma pessoa com dificuldades de leitura ou escrita em telas, quero ditar minha pergunta pelo microfone e ouvir a resposta oficial em áudio de forma clara.

**Critérios de Aceite:**
1. Botão de microfone aciona o reconhecimento de voz nativo do navegador no idioma selecionado.
2. Cada resposta do assistente possui um botão de alto-falante para reproduzir o texto em voz alta.

### User Story 3 - Visualização de Fontes Oficiais e Alerta da Regra de Ouro (P1)
Como um usuário buscando segurança jurídica, quero ver quais leis e portarias oficiais foram usadas para gerar a resposta, e ver um aviso claro com telefones de ONGs quando a informação não estiver disponível.

**Critérios de Aceite:**
1. Respostas com fontes locais ou web exibem cards expansíveis com o título da fonte e link para o portal oficial (`.gov.br`, `DPU`, `ACNUR`).
2. Respostas sob a Regra de Ouro são destacadas visualmente com caixa de acolhimento e contatos rápidos de apoio comunitário.

### User Story 4 - Instalação PWA e Suporte Offline (P2)
Como um usuário de smartphone com pacote de dados instável, quero instalar o aplicativo na tela inicial e ser informado caso a conexão caia sem perder meu histórico de mensagens.

**Critérios de Aceite:**
1. O aplicativo possui manifesto PWA válido (`manifest.json`) e ícones otimizados.
2. Service Worker (`sw.js`) realiza cache dos assets estáticos essenciais.
