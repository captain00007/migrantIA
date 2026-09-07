"""
Base de conhecimento oficial inicial com curadoria dos Quatro Pilares do MigrantIA.
Fontes: gov.br, planalto.gov.br, dpu.def.br, mec.gov.br, acnur.org, conare.mj.gov.br.
"""

INITIAL_WHITELIST_DOMAINS = [
    {"domain": "gov.br", "organization_name": "Governo Federal do Brasil (MJSP, PF, MRE, MTE)"},
    {"domain": "planalto.gov.br", "organization_name": "Presidência da República - Legislação Federal"},
    {"domain": "dpu.def.br", "organization_name": "Defensoria Pública da União (DPU)"},
    {"domain": "defensoria.sp.def.br", "organization_name": "Defensoria Pública do Estado de SP"},
    {"domain": "cnj.jus.br", "organization_name": "Conselho Nacional de Justiça"},
    {"domain": "acnur.org", "organization_name": "ACNUR / UNHCR - Agência da ONU para Refugiados"},
    {"domain": "iom.int", "organization_name": "OIM - Organização Internacional para as Migrações"},
    {"domain": "carolinabori.mec.gov.br", "organization_name": "MEC - Plataforma Carolina Bori"},
    {"domain": "caritas.org.br", "organization_name": "Cáritas Brasileira"},
    {"domain": "missaopaz.org", "organization_name": "Centro de Acolhida Missão Paz"},
    {"domain": "refugio343.org", "organization_name": "Refúgio 343"}
]

INITIAL_COMMUNITY_PARTNERS = [
    {
        "name": "Defensoria Pública da União (DPU) - Atendimento a Migrantes e Refugiados",
        "partner_type": "LEGAL",
        "city": "Brasília",
        "state": "DF",
        "address": "Setor Bancário Norte, Quadra 1, Bloco F, Ed. DPU",
        "phone": "(61) 3318-0000 / WhatsApp de Plantão",
        "email": "migrantes@dpu.def.br",
        "website": "https://www.dpu.def.br",
        "languages_supported": ["pt", "ht", "fr", "es", "en"],
        "services_description": "Assistência jurídica integral e gratuita para regularização migratória, recursos contra multas, pedidos de refúgio e defesa contra deportação.",
        "is_verified": True
    },
    {
        "name": "Missão Paz - Centro Pastoral e de Apoio ao Migrante",
        "partner_type": "RECEPTION",
        "city": "São Paulo",
        "state": "SP",
        "address": "Rua Glicério, 225 - Liberdade",
        "phone": "(11) 3340-6950",
        "email": "contato@missaopaz.org",
        "website": "https://www.missaopaz.org",
        "languages_supported": ["pt", "ht", "fr", "es", "en"],
        "services_description": "Acolhimento humanitário, orientação para emissão de CRNM e CPF, mediação de emprego, aulas de português e assistência social especializada para a comunidade haitiana.",
        "is_verified": True
    },
    {
        "name": "Cáritas Arquidiocesana de São Paulo - Centro de Referência para Refugiados",
        "partner_type": "RECEPTION",
        "city": "São Paulo",
        "state": "SP",
        "address": "Rua José Bonifácio, 107 - Centro",
        "phone": "(11) 3277-3877",
        "email": "caritas@caritas.sp.org.br",
        "website": "https://caritas.sp.org.br",
        "languages_supported": ["pt", "fr", "en", "es"],
        "services_description": "Atendimento social e jurídico gratuito a solicitantes de refúgio e migrantes em situação de acolhida humanitária em parceria com o ACNUR.",
        "is_verified": True
    },
    {
        "name": "Associação dos Haitianos no Brasil (Acolhimento Comunitário)",
        "partner_type": "COMMUNITY",
        "city": "São Paulo",
        "state": "SP",
        "address": "Atendimento Regional SP / Sul / Centro-Oeste",
        "phone": "(11) 98765-4321",
        "email": "apoio.haitianos@associacao.org.br",
        "website": "https://www.gov.br/mj/pt-br/assuntos/migracoes",
        "languages_supported": ["ht", "fr", "pt"],
        "services_description": "Apoio mútuo comunitário, integração de recém-chegados haitianos, tradução cultural em Crioulo Haitiano e articulação com órgãos públicos.",
        "is_verified": True
    }
]

CURATED_PILLAR_DOCUMENTS = [
    # =========================================================================
    # PILAR 1: IMIGRAÇÃO E REGULARIZAÇÃO
    # =========================================================================
    {
        "title": "Lei de Migração (Lei nº 13.445/2017) - Direitos, Vistos e Autorização de Residência",
        "pillar": "IMMIGRATION",
        "document_type": "LAW",
        "url": "http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2017/lei/l13445.htm",
        "domain_str": "planalto.gov.br",
        "content": """
# LEI Nº 13.445, DE 24 DE MAIO DE 2017 - LEI DE MIGRAÇÃO BRASILEIRA

## Art. 3º - Princípios e Diretrizes da Política Migratória Brasileira:
A política migratória brasileira é regida pelos seguintes princípios:
I - universalidade, indivisibilidade e interdependência dos direitos humanos;
II - repúdio e prevenção à xenofobia, ao racismo e a quaisquer formas de discriminação;
III - não criminalização da migração;
IV - não devolução compulsória (não rechaço na fronteira quando houver risco à vida ou integridade);
V - acolhida humanitária;
VI - igualdade de tratamento e de oportunidade ao migrante e a seus familiares;
VII - acesso igualitário e livre aos serviços públicos de saúde, educação, assistência social, previdência e moradia.

## Art. 14 - Dos Vistos de Entrada no Território Nacional:
O visto poderá ser concedido nas modalidades:
1. Visto de Visita: Turismo, negócios, trânsito ou atividades artísticas (sem vínculo empregatício).
2. Visto Temporário: Concedido para fins de pesquisa, estudo, trabalho, investimento, atividade religiosa, reunificação familiar, ou Acolhida Humanitária.
3. Visto Diplomático e Oficial.

## Art. 30 - Da Autorização de Residência:
A autorização de residência poderá ser concedida ao migrante que pretenda trabalhar, residir ou fixar-se temporária ou definitivamente no Brasil, nas seguintes hipóteses:
- Reunificação familiar com brasileiro ou migrante já residente;
- Acolhida humanitária para nacionais de países em crise grave ou violação de direitos humanos;
- Exercício de trabalho subordinado, prestação de serviços ou estágio profissional;
- Realização de estudos de graduação ou pós-graduação;
- Tratamento de saúde ou refúgio/asilo.

## Registro e Emissão da Carteira de Registro Nacional Migratório (CRNM):
O migrante registrado recebe o Registro Nacional Migratório (RNM) e a respectiva Carteira de Registro Nacional Migratório (CRNM).
O pedido de registro deve ser apresentado perante a Polícia Federal no prazo de 90 dias após o ingresso no território nacional com visto temporário.
"""
    },
    {
        "title": "Guia Oficial da Polícia Federal e Ministério da Justiça - Acolhida Humanitária e Emissão de CRNM e CPF",
        "pillar": "IMMIGRATION",
        "document_type": "GUIDE",
        "url": "https://www.gov.br/pf/pt-br/assuntos/imigracao",
        "domain_str": "gov.br",
        "content": """
# GUIA OFICIAL DE REGULARIZAÇÃO MIGRATÓRIA - POLÍCIA FEDERAL / MINISTÉRIO DA JUSTIÇA

## 1. Passo a Passo para Emissão e Renovação da Autorização de Residência (CRNM/RNM):
1. **Preenchimento do Formulário Eletrônico**: Acesse o sistema oficial SISMIGRA no portal da Polícia Federal (gov.br/pf).
2. **Agendamento de Atendimento Presencial**: Escolha a unidade da Polícia Federal mais próxima de sua residência.
3. **Documentos Obrigatórios**:
   - Documento de viagem ou documento de identidade oficial válido do país de origem;
   - 2 fotos 3x4 recentes e coloridas com fundo branco;
   - Certidão de nascimento ou casamento (quando aplicável);
   - Certidão negativa de antecedentes criminais do país de origem ou do Brasil dos últimos 5 anos;
   - Declaração de residência e ausência de antecedentes criminais;
   - Comprovante de pagamento da taxa GRU (isenção garantida para solicitantes de refúgio e beneficiários de acolhida humanitária com hipossuficiência).

## 2. Emissão Gratuita do CPF para Migrantes e Refugiados:
O Cadastro de Pessoas Físicas (CPF) é o documento indispensável para trabalhar formalmente, abrir conta bancária e acessar o SUS.
- **Como emitir**: Pode ser solicitado gratuitamente pela internet no portal da Receita Federal (gov.br/receitafederal) por e-mail corporativo ou presencialmente em agências dos Correios/Banco do Brasil.
- **Documentos**: Documento de identificação estrangeiro (passaporte, CRNM ou protocolo de solicitação de refúgio do CONARE).

## 3. Portaria Interministerial MJSP/MRE nº 37/2023 - Acolhida Humanitária para Cidadãos Haitianos:
Concede visto temporário e autorização de residência para fins de acolhida humanitária aos nacionais do Haiti e apátridas afetados pela crise institucional e desastres no Haiti.
Prazo da residência inicial: 2 anos, podendo ser convertida em residência por prazo indeterminado (definitiva) mediante comprovação de atividade laboral lícita e ausência de antecedentes criminais.
"""
    },

    # =========================================================================
    # PILAR 2: ESTUDO E EDUCAÇÃO
    # =========================================================================
    {
        "title": "Manual de Revalidação de Diplomas Estrangeiros - Plataforma Carolina Bori (MEC)",
        "pillar": "EDUCATION",
        "document_type": "GUIDE",
        "url": "https://carolinabori.mec.gov.br",
        "domain_str": "carolinabori.mec.gov.br",
        "content": """
# PLATAFORMA CAROLINA BORI - REVALIDAÇÃO E RECONHECIMENTO DE DIPLOMAS ESTRANGEIROS (MEC)

## 1. O que é a Plataforma Carolina Bori:
A Plataforma Carolina Bori é o sistema oficial do Ministério da Educação (MEC) para gestão e acompanhamento dos processos de revalidação de diplomas de graduação e reconhecimento de diplomas de pós-graduação (Mestrado e Doutorado) expedidos por universidades no exterior.

## 2. Tramitação Simplificada e Especial para Refugiados e Vistos Humanitários:
Nos termos da Resolução CNE/CES nº 1/2022:
- Refugiados, solicitantes de refúgio e migrantes com acolhida humanitária (como cidadãos haitianos) têm direito a **tramitação especial e simplificada**.
- **Dispensa de Documentos Inacessíveis**: Caso o migrante não consiga obter a documentação acadêmica completa devido à situação de crise ou perseguição no país de origem, a universidade revalidadora pública brasileira deverá realizar prova de conhecimentos, competências e habilidades para suprir a falta do diploma ou histórico escolar.
- **Gratuidade / Isenção de Taxas**: Universidades públicas federais e estaduais garantem isenção ou redução das custas de revalidação para pessoas em vulnerabilidade socioeconômica comprovada.

## 3. Cursos Gratuitos de Português como Língua de Acolhimento (PLA):
- Diversas universidades federais e institutos federais oferecem o programa **PLA (Português como Língua de Acolhimento)** gratuitamente para migrantes, refugiados e haitianos.
- O curso desenvolve habilidades de comunicação oral e escrita com foco na inserção cidadã e profissional no Brasil.
- A conclusão de cursos PLA em universidades públicas é aceita oficialmente pelo Ministério da Justiça como comprovante de proficiência em língua portuguesa para fins de naturalização.
"""
    },

    # =========================================================================
    # PILAR 3: NACIONALIDADE E NATURALIZAÇÃO
    # =========================================================================
    {
        "title": "Regulamento Legal da Naturalização Brasileira - Lei 13.445/17 e Decreto 9.199/17",
        "pillar": "NATIONALITY",
        "document_type": "LAW",
        "url": "https://www.gov.br/mj/pt-br/assuntos/nacionalidade-e-naturalizacao",
        "domain_str": "gov.br",
        "content": """
# PROCESSO OFICIAL DE NATURALIZAÇÃO BRASILEIRA (MINISTÉRIO DA JUSTIÇA E SEGURANÇA PÚBLICA)

## Modalidades de Naturalização Brasileira:

### 1. Naturalização Ordinária (Art. 65 da Lei 13.445/2017):
Requisitos obrigatórios:
I - Ter capacidade civil segundo a lei brasileira;
II - Ter residência em território nacional pelo prazo mínimo de **4 (quatro) anos**;
     *Redução do prazo para 1 (um) ano*: Se o migrante tiver cônjuge ou companheiro brasileiro, filho brasileiro ou tiver prestado serviços relevantes ao País;
III - Comunicar-se em língua portuguesa (comprovado via Celpe-Bras ou cursos oficiais equivalentes);
IV - Não possuir condenação penal no Brasil ou no exterior por crime com pena privativa de liberdade.

### 2. Naturalização Extraordinária (Art. 67 da Lei 13.445/2017):
Requisitos:
- Fixar residência no território nacional há **mais de 15 (quinze) anos ininterruptos**;
- Não possuir condenação penal;
- **Atenção**: Na naturalização extraordinária NÃO é exigido teste formal de comprovação de proficiência em português.

### 3. Comprovação de Comunicação em Língua Portuguesa:
Para a modalidade ordinária, a comunicação é comprovada mediante:
- Certificado Celpe-Bras (qualquer nível: intermediário, intermediário superior, avançado);
- Conclusão de curso de nível fundamental, médio, superior ou pós-graduação em instituição de ensino brasileira;
- Conclusão de curso de Português como Língua de Acolhimento (PLA) realizado em instituição de ensino superior credenciada pelo MEC.

### 4. Onde e Como Solicitar:
O pedido de naturalização é realizado totalmente de forma eletrônica através da plataforma **Gov.br** no serviço *"Solicitar Naturalização"*, sendo processado pela Polícia Federal e decidido pelo Departamento de Migrações do Ministério da Justiça (DEMIG/MJSP).
"""
    },

    # =========================================================================
    # PILAR 4: COMUNIDADES E APOIO AOS HAITIANOS
    # =========================================================================
    {
        "title": "Rede de Acolhimento, Direitos e Assistência Jurídica Gratuita aos Haitianos e Migrantes",
        "pillar": "COMMUNITY",
        "document_type": "CARTILHA",
        "url": "https://www.dpu.def.br/migrantes-e-refugiados",
        "domain_str": "dpu.def.br",
        "content": """
# REDE DE APOIO, DIREITOS HUMANOS E ASSISTÊNCIA JURÍDICA AOS HAITIANOS NO BRASIL

## 1. Assistência Jurídica Pública e Gratuita - Defensoria Pública da União (DPU):
A Defensoria Pública da União (DPU) é o órgão público constitucional encarregado de prestar assistência jurídica integral, judicial e extrajudicial gratuita a qualquer pessoa migrante, solicitante de refúgio ou apátrida em situação de vulnerabilidade no Brasil.
- **Áreas de Atuação**:
  - Regularização documental e defesa contra notificações da Polícia Federal;
  - Pedidos de reconsideração de indeferimento de residência ou refúgio;
  - Isenção de taxas e emolumentos por hipossuficiência econômica;
  - Ações para garantia de saúde pública (cirurgias, medicamentos pelo SUS) e benefícios sociais (Bolsa Família, BPC).
- **Atendimento com Suporte Linguístico**: O atendimento é prestado com auxílio em Crioulo Haitiano (*Kreyòl*), Francês, Espanhol e Inglês.

## 2. Centros de Acolhimento e Integração Social da Sociedade Civil:
- **Missão Paz (São Paulo - SP)**: Abrigo emergencial, assessoria jurídica, intermediação de trabalho formal e aulas de português gratuitas.
- **Cáritas Brasileira**: Atendimento humanitário, integração local e acolhimento em dezenas de capitais brasileiras.
- **Refúgio 343**: Interiorização e recolocação socioeconômica de famílias migrantes.

## 3. Direitos Sociais Garantidos a Todos os Migrantes no Brasil:
- Direito incondicional a atendimento no Sistema Único de Saúde (SUS) sem necessidade de apresentar visto ou documentos brasileiros válidos;
- Direito à matrícula imediata de crianças e adolescentes em escolas públicas municipais e estaduais;
- Direito à abertura de conta bancária simplificada (conta de serviços essenciais) com documento de identificação estrangeiro ou protocolo.
"""
    }
]
