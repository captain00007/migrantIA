# Feature Specification: Chat de Orientação e Consulta Multilíngue para Migrantes (Quatro Pilares)

**Feature Branch**: `001-multilingual-migrant-chat`

**Created**: 2026-09-05

**Last Updated**: 2026-09-05

**Status**: Draft

**Input**: User description: "O sistema que é o chat é capaz de responder o usuário em qualquer idioma, porque é uma IA, e o usuário é capaz de perguntar em qualquer idioma. A interface do sistema tem os 5 idiomas: Crioulo Haitiano, Francês, Inglês, Espanhol e Português. Lembrando os 4 pilares: Imigração e Regularização, Estudo e Educação, Nacionalidade e Naturalização, Comunidades e Apoio aos Haitianos."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consulta de Regularização Migratória e Emissão de Documentos (Priority: P1)

Como uma pessoa migrante ou solicitante de refúgio, quero perguntar sobre como obter ou renovar minha autorização de residência, agendar atendimento na Polícia Federal e emitir meus documentos essenciais (CRNM/RNM, CPF) no meu próprio idioma, para que eu possa viver e trabalhar legalmente no Brasil com informações oficiais e confiáveis.

**Why this priority**: A regularidade documental é a necessidade mais urgente e crítica de qualquer pessoa migrante ao chegar ou permanecer no país, sendo o pré-requisito fundamental para acesso a emprego, moradia e serviços públicos.

**Independent Test**: Pode ser testado enviando perguntas em qualquer idioma (ex: Crioulo Haitiano, Francês, Espanhol, Inglês, Português, etc.) sobre prazos de renovação de visto, trâmites do CRNM na Polícia Federal ou obtenção de CPF, verificando se o sistema entrega respostas precisas, no mesmo idioma do usuário, com links oficiais governamentais e sem alucinações.

**Acceptance Scenarios**:

1. **Given** um usuário acessando o chat sem cadastro prévio, **When** ele pergunta em Português "Como faço para renovar minha autorização de residência por acolhida humanitária?", **Then** o sistema retorna as etapas detalhadas do procedimento oficial, a lista de documentos necessários, o link oficial para agendamento na Polícia Federal e a citação da portaria/norma aplicável.
2. **Given** uma pessoa haitiana perguntando em Crioulo Haitiano (*Kreyòl*) "Kouman mwen ka jwenn CPF mwen an Brezil?", **Then** o sistema responde fluentemente em Crioulo Haitiano explicando o passo a passo da emissão do CPF na Receita Federal / Correios, com instruções claras e links oficiais.
3. **Given** um solicitante hispanofalante perguntando em Espanhol "Cuáles son los requisitos para la autorización de residencia por reunificación familiar?", **Then** o sistema responde em Espanhol detalhando os requisitos e links oficiais da Polícia Federal.
4. **Given** uma pergunta sobre taxas ou prazos que foram alterados recentemente pelo Ministério da Justiça, **When** o usuário consulta o sistema, **Then** o sistema busca os dados oficiais mais recentes na lista de fontes homologadas e apresenta os valores e links diretos atualizados.

---

### User Story 2 - Orientação Educacional, Validação de Diplomas e Cursos de Português (Priority: P2)

Como uma pessoa migrante que deseja continuar seus estudos ou exercer sua profissão, quero consultar como revalidar meu diploma estrangeiro (Plataforma Carolina Bori), ingressar no ensino superior público e encontrar cursos gratuitos de Português como Língua de Acolhimento (PLA), para que eu possa me qualificar e reconstruir minha carreira no Brasil.

**Why this priority**: A inserção educacional e o domínio do idioma são alicerces essenciais para a autonomia socioeconômica e dignidade dos migrantes.

**Independent Test**: Pode ser testado enviando consultas sobre revalidação de diplomas de graduação/pós-graduação, vestibulares para refugiados e matrículas em cursos de português para estrangeiros, validando se as orientações acadêmicas e institucionais oficiais são fornecidas corretamente no idioma do usuário.

**Acceptance Scenarios**:

1. **Given** um usuário que possui diploma emitido no exterior, **When** ele pergunta em Francês "Comment puis-je faire reconnaître mon diplôme universitaire au Brésil?", **Then** o sistema responde em Francês explicando o funcionamento da Plataforma Carolina Bori, as regras de tramitação simplificada para refugiados/humanitários e o portal oficial de submissão.
2. **Given** um usuário anglófono perguntando em Inglês "Where can I find free Portuguese language classes for migrants?", **Then** o sistema responde em Inglês explicando os programas de Português como Língua de Acolhimento (PLA) em universidades públicas e institutos federais, informando canais oficiais de inscrição.

---

### User Story 3 - Esclarecimento de Requisitos e Processos de Naturalização Brasileira (Priority: P3)

Como um residente migrante de longa permanência, quero verificar se cumpro os critérios para solicitar a nacionalidade e naturalização brasileira (ordinária, extraordinária, especial ou provisória), compreendendo prazos, exigências de proficiência em língua portuguesa (como o Celpe-Bras) e etapas de solicitação no Ministério da Justiça.

**Why this priority**: A naturalização consolida a plena cidadania e segurança jurídica do migrante após anos de residência e integração no Brasil.

**Independent Test**: Pode ser testado submetendo cenários de tempo de residência (ex: 4 anos ordinária, 15 anos extraordinária, ou redução para 1 ano por casamento/filhos) e verificando se o sistema calcula e orienta com base na Lei de Migração (Lei 13.445/2017) e decretos regulamentadores.

**Acceptance Scenarios**:

1. **Given** um residente com 4 anos de residência contínua, **When** ele pergunta quais são as exigências para naturalização ordinária, **Then** o sistema detalha os requisitos da Lei nº 13.445/2017 (tempo de residência, ausência de condenação penal, capacidade de comunicação em língua portuguesa) e os comprovantes aceitos (incluindo Celpe-Bras e certificados oficiais).
2. **Given** uma pessoa que reside há mais de 15 anos no Brasil, **When** ela pergunta sobre naturalização extraordinária, **Then** o sistema esclarece os critérios diferenciados (não exigência de teste formal de idioma, apenas comprovação de residência e idoneidade) e indica como dar entrada digitalmente via portal oficial do Governo Federal.

---

### User Story 4 - Diretório de Apoio Comunitário, Assistência Jurídica Gratuita e Acolhimento aos Haitianos (Priority: P4)

Como um migrante haitiano ou em situação de vulnerabilidade, quero encontrar contatos e endereços de associações comunitárias, organizações da sociedade civil (Cáritas, Missão Paz, Refúgio 343) e assistência jurídica pública gratuita (Defensoria Pública da União - DPU), para que eu possa receber apoio presencial especializado e acolhimento cultural.

**Why this priority**: Informações jurídicas e trâmites digitais muitas vezes exigem suporte humano presencial, representação legal gratuita ou acolhimento emergencial, especialmente para a comunidade haitiana.

**Independent Test**: Pode ser testado solicitando contatos de órgãos de assistência gratuita ou associações em uma localidade específica (ou de âmbito nacional), verificando se contatos verificados e canais de atendimento da DPU/ONGs são entregues no idioma do usuário.

**Acceptance Scenarios**:

1. **Given** um migrante haitiano solicitando ajuda jurídica em Crioulo Haitiano para uma notificação da Polícia Federal, **When** ele escreve no chat, **Then** o sistema fornece o contato e canal de atendimento da Defensoria Pública da União (DPU) e das instituições parceiras de acolhimento em Crioulo Haitiano e Português.
2. **Given** uma solicitação sobre onde encontrar assistência social e acolhimento para recém-chegados, **When** o usuário consulta o chat, **Then** o sistema apresenta a lista verificada de organizações parceiras (com telefone, endereço e especialidade de atendimento).

---

### User Story 5 - Navegação e Seleção de Idioma na Interface do Sistema (Priority: P5)

Como uma pessoa migrante acessando a plataforma, quero poder escolher o idioma da interface entre os 5 idiomas disponíveis (Crioulo Haitiano, Francês, Inglês, Espanhol e Português), para que todos os botões, menus, orientações e avisos institucionais sejam exibidos de forma compreensível e acolhedora.

**Why this priority**: A interface amigável no idioma materno do migrante elimina barreiras de navegação e transmite segurança e acessibilidade imediata.

**Independent Test**: Pode ser testado alternando o seletor de idiomas entre os 5 idiomas oficiais da interface e verificando se 100% dos textos visuais, rótulos de botões, banners de aviso legal e placeholders são traduzidos instantaneamente.

**Acceptance Scenarios**:

1. **Given** um usuário que prefere navegar em Crioulo Haitiano, **When** ele seleciona "Kreyòl Ayisyen" no seletor de idioma da interface, **Then** todos os elementos visuais (cabeçalho, botões de ação, campo de texto, aviso da Regra de Ouro) são exibidos em Crioulo Haitiano.
2. **Given** um usuário navegando em Espanhol, Francês ou Inglês, **When** ele clica no seletor correspondente, **Then** a interface atualiza toda a linguagem estática da aplicação para o idioma selecionado.

---

### User Story 6 - Resposta Transparente Diante de Informações Inexistentes ou Não Homologadas (Regra de Ouro) (Priority: P6)

Como um usuário fazendo uma pergunta sobre um caso jurídico complexo não documentado ou sobre um boato/procedimento não oficial, quero que o sistema declare explicitamente que não possui a informação em fontes oficiais em vez de especular ou inventar uma resposta, para que eu nunca tome decisões jurídicas arriscadas baseadas em orientações falsas.

**Why this priority**: A segurança jurídica e a integridade da vida do migrante exigem tolerância zero a alucinações ou conselhos não verificados.

**Independent Test**: Pode ser testado perguntando sobre rumores de anistia inexistentes, taxas fictícias ou casos jurídicos individuais atípicos em qualquer idioma, verificando se o sistema aciona a resposta padrão de transparência e indica os órgãos competentes.

**Acceptance Scenarios**:

1. **Given** uma pergunta sobre um suposto "perdão geral de multas para migrantes sem portaria publicada", **When** o sistema não encontra base em fontes oficiais homologadas, **Then** ele responde com transparência no idioma da pergunta: declara que a informação não consta nos canais oficiais consultados, não inventa procedimentos e orienta a consulta direta à Defensoria Pública da União ou à Polícia Federal.

---

### Edge Cases

- **Interação do Chat em Idiomas Adicionais**: O usuário envia perguntas em idiomas além dos 5 principais da interface (ex: Árabe, Russo, Mandarim, Alemão). A IA do chat deve compreender e responder com precisão no idioma utilizado pelo usuário, mantendo a fundamentação estrita em fontes oficiais brasileiras.
- **Mistura de idiomas na mesma mensagem (Code-switching)**: O usuário escreve termos em português misturados com Crioulo Haitiano ou Francês (ex: "Kouman mwen renouvle autorização de residência na PF?"). O sistema deve compreender o contexto e responder preferencialmente no idioma predominante da pergunta de forma clara.
- **Consultas fora de escopo (ex: receitas culinárias, conselhos de investimento)**: O sistema deve educadamente recusar e redirecionar o usuário para os temas cobertos pelos Quatro Pilares do MigrantIA.
- **Tentativas de contornar fontes ou solicitar conselhos informais ("Dá um jeitinho", "Como entrar sem documentos?")**: O sistema deve manter estrita adesão aos caminhos legais oficiais, informando os direitos de solicitação de refúgio e acolhida humanitária garantidos pela legislação brasileira, sem violar a lei.
- **Quedas temporárias ou lentidão de conectividade externa**: O sistema deve priorizar as informações da base local de conhecimento consolidada e avisar caso consultas a links em tempo real estejam indisponíveis no momento.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer atendimento conversacional interativo cobrindo integralmente os Quatro Pilares de Conhecimento: (1) Imigração e Regularização, (2) Estudo e Educação, (3) Nacionalidade e Naturalização, e (4) Comunidades e Apoio aos Haitianos.
- **FR-002**: A IA conversacional do chat DEVE ser capaz de receber perguntas e responder fluentemente em qualquer idioma natural utilizado pelo usuário, identificando e espelhando automaticamente a língua de interlocução.
- **FR-003**: A interface gráfica do usuário (UI / PWA) DEVE disponibilizar internacionalização completa (i18n) e permitir a alternância dinâmica entre os 5 idiomas oficiais do sistema: (1) Crioulo Haitiano (*Kreyòl Ayisyen*), (2) Francês (*Français*), (3) Inglês (*English*), (4) Espanhol (*Español*) e (5) Português (*Português*).
- **FR-004**: O sistema DEVE permitir uso totalmente anônimo e imediato através de sessões temporárias, sem exigir criação de conta, login ou fornecimento de documentos pessoais.
- **FR-005**: O sistema DEVE fundamentar todas as respostas da IA exclusivamente em fontes oficiais homologadas (legislação nacional, portarias ministeriais, dados governamentais, organismos internacionais ACNUR/OIM, Defensoria Pública e entidades cadastradas de acolhimento).
- **FR-006**: O sistema DEVE incluir citações explícitas com títulos e links diretos para as fontes oficiais que embasam as orientações fornecidas em cada resposta.
- **FR-007**: O sistema DEVE aplicar a "Regra de Ouro" de transparência: quando uma informação solicitada não constar em fontes oficiais homologadas ou for inconclusiva, o sistema DEVE emitir uma resposta padronizada no idioma do usuário declarando a ausência de registro oficial e indicando o contato com a Defensoria Pública da União (DPU) ou instituições de acolhimento verificadas.
- **FR-008**: O sistema DEVE disponibilizar o diretório estruturado de organizações de acolhimento, associações de haitianos e postos de atendimento da Defensoria Pública, informando localização, serviços prestados, idiomas suportados e formas de contato.
- **FR-009**: O sistema DEVE manter o histórico de mensagens ativo durante toda a sessão do usuário, permitindo perguntas de acompanhamento e refinamento da dúvida contextual.
- **FR-010**: O sistema DEVE bloquear qualquer recomendação de fontes externas não pertencentes à lista estrita de domínios homologados.

### Key Entities *(include if feature involves data)*

- **Sessão Anônima (Anonymous Session)**: Canal de conversa efêmero do usuário, contendo identificador único anônimo, idioma selecionado na interface (um dos 5 idiomas oficiais) e histórico de interações temporário.
- **Mensagem de Interação (Chat Message)**: Registro de pergunta do usuário e resposta gerada pela IA, incluindo timestamp, idioma detectado da mensagem, lista de fontes oficiais citadas e indicador de acionamento da Regra de Ouro.
- **Pilar de Conhecimento (Knowledge Pillar)**: Categoria temática que classifica os tópicos (Imigração/Regularização, Estudo/Educação, Nacionalidade/Naturalização, Comunidade/Apoio aos Haitianos).
- **Fonte Oficial Homologada (Verified Official Source)**: Registro de órgão público, legislação, agência internacional ou ONG autorizada, contendo nome institucional, domínio oficial, pilar associado e escopo de autoridade.
- **Organização de Apoio e Acolhimento (Community & Legal Partner)**: Registro do diretório com nome da entidade, tipo (Jurídico, Acolhimento, Educacional, Comunitário), idiomas atendidos, contatos e endereço.
- **Dicionário de Localização da Interface (UI Translation Resource)**: Conjunto de traduções estruturadas para os 5 idiomas da interface (Kreyòl, Français, English, Español, Português) contemplando todos os textos estáticos da aplicação.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O usuário obtém resposta completa e orientações passo a passo em menos de 5 segundos a partir do envio da pergunta.
- **SC-002**: 100% dos elementos da interface gráfica estão perfeitamente traduzidos e adaptados nos 5 idiomas oficiais (Crioulo Haitiano, Francês, Inglês, Espanhol e Português).
- **SC-003**: A IA do chat responde com sucesso no idioma de envio do usuário em 100% dos testes de interação multilíngue.
- **SC-004**: 100% das respostas geradas contêm links e citações verificáveis provenientes exclusivamente de fontes oficiais homologadas.
- **SC-005**: 0% de ocorrência de alucinações ou invenções normativas (índice de fidelidade/groundedness de 100% em testes de avaliação).
- **SC-006**: 100% das perguntas sobre temas não constantes nas fontes oficiais ativam a Regra de Ouro com direcionamento transparente para órgãos competentes / DPU.
- **SC-007**: Os usuários conseguem iniciar consultas e alternar idiomas imediatamente na primeira visita sem necessidade de cadastro em 100% dos acessos.

## Assumptions

- O usuário possui acesso à internet (web/mobile) para interagir com a interface de chat.
- O escopo inicial foca em orientações textuais informativas, não realizando submissões de formulários em nome do usuário em sistemas de terceiros (ex: o sistema fornece o link e instrução para o agendamento na PF, mas o agendamento em si é realizado pelo próprio usuário no site da Polícia Federal).
- As orientações têm caráter informativo e de acolhimento, mantendo sempre o aviso de que não substituem a assistência jurídica individual formal de defensores públicos ou advogados habilitados.
- Os domínios governamentais e de instituições parceiras constantes na lista oficial estão acessíveis e em operação.
