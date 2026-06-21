# DaTabela — Frontend 🏀

Este documento é a documentação técnica principal e o guia de referência definitivo da pasta `frontend/` do **DaTabela**.

Ele explica o papel do frontend dentro do ecossistema do projeto, a relação de dados com os módulos `/backend` e `/data`, a pilha de tecnologias utilizada, as decisões de design, a estrutura limpa de arquivos, a arquitetura de roteamento físico, a lógica das principais telas e componentes, e os procedimentos operacionais para execução local, testes e builds de produção.

---

## 🎯 Sumário

1. [Visão Geral do Módulo](#1-visão-geral-do-módulo)
2. [Papel do Frontend no DaTabela](#2-papel-do-frontend-no-databela)
3. [Arquitetura de Comunicação e Fluxos de Dados](#3-arquitetura-de-comunicação-e-fluxos-de-dados)
4. [Tecnologias Utilizadas e Ecossistema](#4-tecnologias-utilizadas-e-ecossistema)
   * 4.1 [Lista Detalhada de Dependências (package.json)](#41-lista-detalhada-de-dependências-packagejson)
5. [Arquitetura de Roteamento Físico e URLs (Expo Router)](#5-arquitetura-de-roteamento-físico-e-urls-expo-router)
   * 5.1 [Funcionamento das Rotas com Parâmetros Dinâmicos](#51-funcionamento-das-rotas-com-parâmetros-dinâmicos)
   * 5.2 [Comportamento Responsivo: Web vs. Mobile](#52-comportamento-responsivo-web-vs-mobile)
6. [Estrutura Completa de Pastas e Arquivos](#6-estrutura-completa-de-pastas-e-arquivos)
7. [Dicionário Exaustivo de Arquivos do Projeto (File-by-File)](#7-dicionário-exaustivo-de-arquivos-do-projeto-file-by-file)
   * 7.1 [Pasta `src/api/` (Integração REST e Clientes)](#71-pasta-srcapi-integração-rest-e-clientes)
   * 7.2 [Pasta `src/app/` (Páginas e Entradas Físicas)](#72-pasta-srcapp-páginas-e-entradas-físicas)
   * 7.3 [Pasta `src/components/` (UI, Layout e Data)](#73-pasta-srccomponents-ui-layout-e-data)
   * 7.4 [Pasta `src/features/` (Estruturas Lógicas das Telas)](#74-pasta-srcfeatures-estruturas-lógicas-das-telas)
   * 7.5 [Pasta `src/hooks/` (Compartilhamento de Lógica)](#75-pasta-srchooks-compartilhamento-de-lógica)
   * 7.6 [Pasta `src/theme/` (Design System Dark e Tokens)](#76-pasta-srctheme-design-system-dark-e-tokens)
   * 7.7 [Pasta `src/types/` (Contratos TypeScript)](#77-pasta-srctypes-contratos-typescript)
   * 7.8 [Pasta `src/utils/` (Formatadores e Dicionário de Basquete)](#78-pasta-srcutils-formatadores-e-dicionário-de-basquete)
   * 7.9 [Arquivo de Estilo Estático (`src/global.css`)](#79-arquivo-de-estilo-estático-srcglobalcss)
8. [Detalhamento de Regras de Negócio por Componente de Feature](#8-detalhamento-de-regras-de-negócio-por-componente-de-feature)
   * 8.1 [HomeScreen (Destaque do Dia e Líderes)](#81-homescreen-destaque-do-dia-e-líderes)
   * 8.2 [PlayerDetailScreen (Médias, Totais e Jogos Filtrados)](#82-playerdetailscreen-médias-totais-e-jogos-filtrados)
   * 8.3 [TeamDetailScreen (Filtro do Saldo de Pontos +/-)](#83-teamdetailscreen-filtro-do-saldo-de-pontos---)
   * 8.4 [RankingsScreen (Top 10 Temporadas)](#84-rankingsscreen-top-10-temporadas)
   * 8.5 [GameDetailScreen (Ficha de Confrontos)](#85-gamedetailscreen-ficha-de-confrontos)
9. [Componentes Complexos do Sistema](#9-componentes-complexos-do-sistema)
   * 9.1 [DynamicTable (Cálculo de Larguras e Alinhamentos)](#91-dynamictable-cálculo-de-larguras-e-alinhamentos)
   * 9.2 [FallbackImage (Iniciais Resilientes)](#92-fallbackimage-iniciais-resilientes)
10. [Mecanismo do Ask AI (Chat de Linguagem Natural)](#10-mecanismo-do-ask-ai-chat-de-inteligência-artificial)
    * 10.1 [Arquitetura de Estados de Resposta](#101-arquitetura-de-estados-de-resposta)
    * 10.2 [Fluxo de Desambiguação (needs_clarification)](#102-fluxo-de-desambiguação-needs_clarification)
11. [Convenções de Desenvolvimento e Padronização](#11-convenções-de-desenvolvimento-e-padronização)
12. [Configuração do Ambiente e API](#12-configuração-do-ambiente-e-api)
13. [Guia de Execução Local](#13-guia-de-execução-local)
14. [Procedimentos de Deploy e Geração de Builds](#14-procedimentos-de-deploy-e-geração-de-builds)
15. [Testes e Checagem Estática de Código](#15-testes-e-checagem-estática-de-código)
16. [Manual de Evolução e Manutenção da Interface](#16-manual-de-evolução-e-manutenção-da-interface)
17. [Diagnóstico de Problemas Comuns (FAQ)](#17-diagnóstico-de-problemas-comuns-faq)
18. [Auditoria de Arquivos Suspeitos](#18-auditoria-de-arquivos-suspeitos)

---

# 1. Visão Geral do Módulo

O frontend do **DaTabela** é uma aplicação multiplataforma responsiva desenvolvida com **Expo** e **React Native**, fornecendo uma interface visual de alto desempenho para consulta de dados estatísticos do basquete profissional brasileiro, com foco nos dados históricos da Liga Nacional de Basquete (LNB) e do Novo Basquete Brasil (NBB).

Por meio de uma base de código unificada escrita em **TypeScript**, o projeto atende perfeitamente a:
*   **Web (Navegadores)**: Desktop e mobile web, otimizado para navegadores modernos com suporte a renderização rápida baseada em flexbox e CSS integrado.
*   **Mobile Nativo (Android e iOS)**: Executável de forma otimizada via compilador do Expo, respeitando as margens físicas de celulares de diversas marcas.

O sistema une a exibição clássica de dados esportivos estruturados com um mecanismo inovador de pesquisa baseado em inteligência artificial (inspirado no *StatMuse*), permitindo que usuários façam perguntas em linguagem natural e recebam tabelas de dados dinâmicas correspondentes como resposta.

---

# 2. Papel do Frontend no DaTabela

No ecossistema do projeto, o frontend representa a **camada de apresentação, interação e controle de desambiguação**. Ele adota as seguintes diretrizes e limites arquiteturais:

*   **Consumo Exclusivo**: O frontend é 100% dependente da API exposta pelo `/backend`. Ele não acessa de forma direta o banco de dados SQLite, arquivos CSV locais ou scripts de raspagem.
*   **Decisões Visuais de Exibição**: O backend entrega dados puros e completos. Cabe ao frontend decidir a melhor forma de apresentá-los (quais colunas esconder em celulares, como aplicar grades de cores a tabelas, ordenação visual de linhas e tratamento de paginações na tela).
*   **Abstração e Tradução**: Converte nomenclatura técnica oriunda do banco de dados (ex: `field_goals_pct`, `offensive_rebounds`) em siglas e abreviações oficiais adotadas pela crônica e torcedores de basquete no Brasil (`FG%`, `OREB`), além de aplicar formatações decimais.
*   **Interatividade Humana**: Controla o fluxo de esclarecimento de buscas (desambiguação), permitindo que o usuário escolha o atleta correto quando uma pergunta livre gerar correspondências duplicadas.

---

# 3. Arquitetura de Comunicação e Fluxos de Dados

O fluxo de dados da aplicação ocorre por meio de requisições HTTP assíncronas assinaladas pelo tipo MIME `application/json`. 

A estrutura de comunicação básica obedece ao seguinte fluxo:

```text
[Usuário Interage] 
       │
       ▼
[Componente de Tela (Feature)] ──► Dispara hook `useAsync`
                                           │
                                           ▼
[API Client (fetch wrapper)] ──────► Envia GET/POST para backend FastAPI
                                           │
                                           ▼
[FastAPI / SQLite (Backend)] ──────► Processa dados e retorna JSON
                                           │
                                           ▼
[API Client (fetch wrapper)] ──(Sucesso)─► Retorna tipagem de modelo estruturado (Player, Team)
       │
       ├─► (Erro: ApiError) ──► Aciona estado visual de erro (ErrorState)
       │
       ▼
[DynamicTable / UI] ──────────► Formata números, traduz siglas e desenha na tela
```

1.  **Montagem da Requisição**: O componente na camada de `features/` inicializa a chamada ao módulo de API correspondente passando parâmetros digitados ou recuperados da URL (como `id` do atleta).
2.  **Execução**: O wrapper `client.ts` injeta a URL base configurada em `config.ts` e efetua a chamada.
3.  **Tratamento de Exceções**: Se o servidor FastAPI estiver desligado ou retornar falhas internas, a exceção `ApiError` é capturada pelo hook `useAsync` que alterna o estado da tela de `loading` para `error`.
4.  **Renderização Dinâmica**: Em cenários de sucesso, o contêiner recebe o array e mapeia as informações estruturadas para o componente de exibição.

---

# 4. Tecnologias Utilizadas e Ecossistema

O DaTabela adota ferramentas modernas para garantir estabilidade, tipagem segura e adaptabilidade de layout:

*   **Expo (v56)**: Framework principal para React Native que unifica as APIs nativas dos dispositivos móveis e simplifica a renderização para a plataforma Web.
*   **React Native Web**: Biblioteca de compatibilidade que converte os componentes primitivos nativos do React Native (`View`, `Text`, `TextInput`, `ScrollView`) em tags HTML5 sem perdas de desempenho.
*   **TypeScript (v6)**: Garante checagem estática rigorosa de tipos, permitindo mapear com segurança os esquemas de respostas JSON do backend FastAPI.
*   **Expo Router**: Sistema de roteamento baseado em arquivos físicos na pasta `src/app/`, fornecendo suporte nativo para navegação por URLs de navegadores e transição suave de abas no ambiente mobile.
*   **Expo Image**: Componente avançado de renderização de imagens que substitui a tag `Image` padrão do React Native, provendo transições suaves de opacidade e gerenciamento de cache de fotos e escudos em dispositivos móveis.
*   **React Native Safe Area Context**: Gerencia o posicionamento de telas prejuízo e margens físicas, evitando conflitos com entalhes de câmeras (notches) e barras de gestos do sistema operacional.

### 4.1 Lista Detalhada de Dependências (package.json)

As dependências de produção registradas e instaladas no projeto são:

*   `@expo/ui` (`~56.0.18`): Provedor de estilos base e helpers de interface do Expo.
*   `expo` (`~56.0.12`): Runtime principal e motor do ecossistema.
*   `expo-constants` (`~56.0.18`): Fornece acesso a constantes de configuração do app configuradas no `app.json`.
*   `expo-device` (`~56.0.4`): Utilitário para verificar especificações físicas do aparelho em execução (identificação de marca, modelo e tipo de dispositivo).
*   `expo-font` (`~56.0.7`): Carregador assíncrono de fontes externas (como Google Fonts).
*   `expo-glass-effect` (`~56.0.4`): Renderizador de efeitos visuais de desfoque (Blur/Glassmorphism) para layouts de menus.
*   `expo-image` (`~56.0.11`): Carregador e cacheador inteligente de fotos e escudos.
*   `expo-linking` (`~56.0.14`): Utilitário para resolver links profundos (Deep Linking) no ambiente mobile nativo.
*   `expo-router` (`~56.2.11`): Gerenciador de navegação baseado no sistema de diretórios.
*   `expo-splash-screen` (`~56.0.10`): Controla a exibição e fechamento da tela de inicialização do aplicativo móvel.
*   `expo-status-bar` (`~56.0.4`): Controla a barra superior de status do celular (hora, bateria, sinal).
*   `expo-symbols` (`~56.0.6`): Biblioteca contendo ícones vetoriais unificados para a aplicação.
*   `expo-system-ui` (`~56.0.5`): Acesso a configurações globais de interface do sistema operacional hospedeiro.
*   `expo-web-browser` (`~56.0.5`): Permite carregar sites externos integrados dentro de webviews móveis.
*   `react` (`19.2.3`) & `react-dom` (`19.2.3`): Biblioteca base para construção de componentes declarativos.
*   `react-native` (`0.85.3`): Biblioteca de compilação de elementos nativos.
*   `react-native-gesture-handler` (`~2.31.1`): Gerenciador de gestos avançados de toque para mobile (arrastar, pinçar, toque duplo).
*   `react-native-reanimated` (`4.3.1`): Motor de alta performance para execução de animações.
*   `react-native-safe-area-context` (`~5.7.0`): Helper para bordas seguras físicas.
*   `react-native-screens` (`4.25.2`): Otimizador de renderização física de transição de telas no Android/iOS.
*   `react-native-web` (`~0.21.0`): Tradutor de elementos nativos do React Native para elementos do DOM HTML.
*   `react-native-worklets` (`0.8.3`): Biblioteca de threads secundárias usada por animações do Reanimated.

---

# 5. Arquitetura de Roteamento Físico e URLs (Expo Router)

O **Expo Router** mapeia arquivos físicos localizados na pasta `src/app/` diretamente para rotas web acessíveis via URL e telas físicas no celular.

### 5.1 Funcionamento das Rotas com Parâmetros Dinâmicos

As pastas que possuem nomes entre colchetes, como `[id]`, representam rotas de parâmetros dinâmicos.
*   Ao navegar para `/players/123` na web, o Expo Router mapeia o componente localizado em `src/app/players/[id].tsx` e fornece o identificador de valor `123` via hook `useLocalSearchParams()`.
*   O mesmo processo ocorre com as fichas de equipes em `src/app/teams/[id].tsx` e detalhes de partidas em `src/app/games/[id].tsx`.

### 5.2 Comportamento Responsivo: Web vs. Mobile

*   **Ambiente Web**: Cada tela possui uma URL correspondente na barra de endereços do navegador (ex: `http://localhost:8081/rankings`), permitindo indexação, compartilhamento direto de links de perfis de atletas e uso seguro dos botões de voltar/avançar do navegador.
*   **Ambiente Mobile**: O roteador opera como um navegador de pilhas nativo (`Stack Navigator`). A transição de telas empilha visualmente a página visitada, oferecendo o gesto clássico de deslizar para voltar nas laterais da tela em smartphones.

---

# 6. Estrutura Completa de Pastas e Arquivos

O diretório do frontend foi higienizado de boilerplates, caches e restos de testes locais. A árvore completa de pastas e arquivos estruturados segue abaixo:

```text
frontend/
├── .env.example                  # Modelo de variáveis de ambiente
├── app.json                      # Manifesto de configuração do Expo (ícones, splash screens)
├── expo-env.d.ts                 # Tipagens automáticas globais do Expo
├── package.json                  # Dependências do Node.js e scripts de automação
├── tsconfig.json                 # Configurações do compilador TypeScript
└── src/
    ├── global.css                # [Suspeito] Definições globais de variáveis de fontes no Expo Web
    ├── api/                      # Camada de comunicação assíncrona com o backend FastAPI
    │   ├── ask.ts                # Requisições do módulo de linguagem natural (/ask)
    │   ├── client.ts             # Cliente HTTP fetch unificado com tratamento de ApiError
    │   ├── config.ts             # Carrega a URL da API do .env com fallbacks locais
    │   ├── games.ts              # Requisições para obter scouts de partidas
    │   ├── players.ts            # Requisições de atletas, recordes e médias
    │   ├── rankings.ts           # Requisições de líderes estatísticos agregados
    │   ├── seasons.ts            # Requisições para listar temporadas
    │   └── teams.ts              # Requisições de dados institucionais de equipes
    ├── app/                      # Roteador físico do Expo Router (Páginas e Layouts)
    │   ├── +not-found.tsx        # Fallback de erro para páginas 404
    │   ├── _layout.tsx           # Layout inicial unificado da aplicação
    │   ├── ask.tsx               # Rota física do chat Ask AI
    │   ├── help.tsx              # Rota física da central de FAQ e ajuda
    │   ├── index.tsx             # Rota física da página inicial
    │   ├── search.tsx            # Rota física da busca global unificada
    │   ├── games/
    │   │   ├── [id].tsx          # Rota física de boxscores de partidas
    │   │   └── index.tsx         # Rota física da lista cronológica de jogos
    │   ├── players/
    │   │   ├── [id].tsx          # Rota física do perfil de jogadores
    │   │   └── index.tsx         # Rota física da listagem de jogadores
    │   ├── rankings/
    │   │   └── index.tsx         # Rota física da tela de rankings de líderes
    │   └── teams/
    │       ├── [id].tsx          # Rota física de perfil e elenco de clubes
    │       └── index.tsx         # Rota física da listagem de clubes
    ├── components/               # Componentes gerais de UI e Layout compartilhados
    │   ├── data/
    │   │   ├── DynamicTable.tsx  # Tabela com rolagem horizontal independente e tradutor de siglas
    │   │   ├── KeyValueList.tsx  # Exibição de dados chave-valor para fichas técnicas
    │   │   └── StatsTable.tsx    # Envoltório de filtragem para omitir colunas técnicas de IDs
    │   ├── layout/
    │   │   ├── AppShell.tsx      # Componente com a estrutura básica de Header e Footer
    │   │   ├── Header.tsx        # Navbar responsiva com menu móvel hambúrguer e busca
    │   │   └── PageContainer.tsx # Centralizador de conteúdo com largura máxima para web
    │   ├── navigation/
    │   │   └── NavLink.tsx       # Link de navegação com marcador de estado ativo
    │   └── ui/
    │       ├── Badge.tsx         # Indicador informativo colorido (V/D, posições)
    │       ├── Button.tsx        # Botão interativo com estados de hover e loading
    │       ├── EmptyState.tsx    # Mensagem de lista ou busca sem correspondências
    │       ├── ErrorState.tsx    # Painel de erro de rede com botão de recarregar
    │       ├── FallbackImage.tsx # Carregador de fotos com fallback em iniciais estilizadas
    │       ├── LoadingState.tsx  # Spinner circular laranja de carregamento
    │       ├── Select.tsx        # Dropdown customizado para filtros em tema escuro
    │       └── TextInput.tsx     # Campo de digitação customizado
    ├── features/                 # Módulos encapsulados de regras de negócios por tela
    │   ├── ask/
    │   │   ├── AskClarification.tsx # Painel com opções de desambiguação de nomes de atletas
    │   │   ├── AskExamples.tsx   # Exemplos sugeridos de perguntas para busca em IA
    │   │   ├── AskInput.tsx      # Barra de envio de perguntas do assistente
    │   │   ├── AskResult.tsx     # Interpretador e desenhador dinâmico de tabelas do /ask
    │   │   ├── AskScreen.tsx     # Tela principal de conversação
    │   │   └── AskStatusMessage.tsx # Status e mensagens informativas do assistente
    │   ├── games/                # Telas de exibição de partidas
    │   │   ├── GameDetailScreen.tsx # Visualização de boxscore e scouts individuais por jogo
    │   │   └── GamesScreen.tsx   # Tela de histórico de jogos e resultados
    │   ├── home/                 # Telas da página inicial
    │   │   ├── HighlightCard.tsx # Destaque do jogador de maior eficiência no último jogo
    │   │   ├── HomeScreen.tsx    # Página principal contendo destaques, líderes e standings
    │   │   ├── LeaderboardCard.tsx # Quadros de líderes estatísticos da temporada
    │   │   └── StandingsWidget.tsx # Tabela resumida de classificação da temporada
    │   ├── players/              # Telas da área de jogadores
    │   │   ├── PlayerCard.tsx    # Mini card descritivo do jogador para a galeria
    │   │   ├── PlayerDetailScreen.tsx # Perfil detalhado, recordes e tabelas analíticas
    │   │   ├── PlayerFilters.tsx # Filtros da galeria de atletas
    │   │   └── PlayersScreen.tsx # Galeria de atletas com paginação
    │   ├── rankings/             # Telas da área de rankings
    │   │   ├── RankingsScreen.tsx # Rankings e filtros
    │   │   └── RankingTable.tsx  # Tabela especializada de posições do campeonato
    │   ├── search/               # Telas do buscador global
    │   │   ├── SearchResults.tsx # Exibição segmentada por times e jogadores
    │   │   └── SearchScreen.tsx  # Tela principal do buscador global
    │   └── teams/                # Telas da área de times
    │       ├── TeamCard.tsx      # Mini card institucional de time para a galeria
    │       ├── TeamDetailScreen.tsx # Perfil descritivo de clubes, títulos e comissão
    │       └── TeamsScreen.tsx   # Galeria de clubes da LNB
    ├── hooks/                    # Hooks reutilizáveis
    │   ├── useAsync.ts           # Facilitador de estados de requisições assíncronas
    │   └── useResponsive.ts      # Verificador de breakpoints em tempo real para web
    ├── theme/                    # Design System Dark do DaTabela
    │   ├── colors.ts             # Constantes cromáticas do tema dark e laranja do NBB
    │   ├── index.ts              # Objeto unificado exportador do tema
    │   ├── spacing.ts            # Tokens numéricos de espaçamentos lógicos
    │   └── typography.ts         # Definições tipográficas e pilhas de fontes de sistema
    ├── types/                    # Tipagens estritas do TypeScript
    │   ├── api.ts                # Definições de envelopes genéricos da API
    │   ├── ask.ts                # Tipagens das respostas geradas pelo assistente
    │   ├── declarations.d.ts     # Tipagem auxiliar para importação de CSS no bundler
    │   └── models.ts             # Entidades de negócio (Player, Team, Game, Standing, etc.)
    └── utils/                    # Funções utilitárias auxiliares
        ├── errors.ts             # Classe Customizada ApiError
        ├── formatters.ts         # Conversores de datas, médias e percentuais
        └── labels.ts             # Conversor e dicionário de siglas de estatísticas de basquete brasileiro
```

---

# 7. Dicionário Exaustivo de Arquivos do Projeto (File-by-File)

Abaixo é apresentado um mapeamento de **cada um dos 74 arquivos** de código que constituem o frontend do DaTabela, contendo explicações técnicas, escopos e responsabilidades.

## 7.1 Pasta `src/api/` (Integração REST e Clientes)

### `client.ts`
*   **Responsabilidade**: Fornecer um wrapper HTTP padronizado baseado no `fetch` nativo. Ele anexa cabeçalhos padrão (`Content-Type: application/json`), resolve caminhos absolutos e intercepta retornos de erro de rede. Se a API responder com códigos HTTP inválidos (400, 500, etc.), o wrapper decodifica a falha e lança uma exceção tipada da classe `ApiError` contendo os detalhes técnicos da resposta.

### `config.ts`
*   **Responsabilidade**: Prover a resolução dinâmica do endereço IP do backend FastAPI. Lê a variável `EXPO_PUBLIC_API_URL` e, caso não exista, fornece o endereço de loopback clássico `http://127.0.0.1:8000`.

### `ask.ts`
*   **Responsabilidade**: Centralizar chamadas de rede da rota experimental `/ask`. Fornece `askQuestion(query)` que consulta `/ask?q=...` e `getAskExamples()` que requisita `/ask/examples` para obter perguntas rápidas de demonstração.

### `players.ts`
*   **Responsabilidade**: Clientes de comunicação da entidade Jogador. Provê `getPlayers(q, teamId, limit, offset)` para buscas e filtros com paginação, `getPlayerDetail(id)` para fichas técnicas, prêmios e recordes, e `getPlayerGames(id, limit, offset)` para resgatar os scouts de confrontos recentes disputados pelo atleta.

### `teams.ts`
*   **Responsabilidade**: Conectar a rota de equipes. Fornece `getTeams()` para listar as equipes participantes e `getTeamDetail(id)` que recupera o ginásio, comissão técnica, títulos, elenco completo e estatísticas históricas agregadas por edições do campeonato.

### `games.ts`
*   **Responsabilidade**: Integração da rota de scouts de confrontos. Fornece `getGameDetail(id)` que traz a pontuação total do jogo, os placares parciais por quarto de tempo e a grade estatística completa de cada jogador envolvido (minutos, pontos, cestas, etc.).

### `rankings.ts`
*   **Responsabilidade**: Conexão com líderes estatísticos consolidados. Fornece `getRankings(seasonId, category)` para obter o Top 10 ordenado de jogadores ou times em métricas específicas.

### `seasons.ts`
*   **Responsabilidade**: Popular caixas de seleção na interface. Fornece `getSeasons()` para requisitar do backend a lista de edições do campeonato cadastradas no banco de dados.

### `search.ts`
*   **Responsabilidade**: Conexão com o buscador global. Fornece `searchGlobal(query)` para consultar `/search?q=...` e obter correspondências parciais de termos de busca.

---

## 7.2 Pasta `src/app/` (Páginas e Entradas Físicas)

### `_layout.tsx`
*   **Responsabilidade**: Inicializador raiz. Envolve as telas em um provedor de área segura de layout móvel (`SafeAreaProvider`), ajusta o estilo da barra de status móvel para luz (`light`) e renders o contêiner de empilhamento de telas (`Stack`).

### `+not-found.tsx`
*   **Responsabilidade**: Página de tratamento 404. Exibida quando rotas inexistentes forem acessadas pelo navegador ou deeplinks quebrados forem chamados, exibindo uma mensagem informativa e link de retorno ao Dashboard inicial.

### `index.tsx`
*   **Responsabilidade**: Rota física da página raiz (`/`). Importa e exporta diretamente a tela de domínio `HomeScreen` envelopada em sua estrutura corporativa.

### `ask.tsx`
*   **Responsabilidade**: Rota física do chat inteligente (`/ask`). Exibe o orquestrador funcional de IA `AskScreen`.

### `search.tsx`
*   **Responsabilidade**: Rota física do buscador global (`/search`). Instancia o componente modular `SearchScreen`.

### `help.tsx`
*   **Responsabilidade**: Central de ajuda e FAQs. Fornece uma interface de leitura limpa esclarecendo o ciclo operacional de dados, atualizações automáticas de standings e suporte do aplicativo.

### `players/index.tsx`
*   **Responsabilidade**: Rota física da galeria geral de jogadores (`/players`). Instancia a feature `PlayersScreen`.

### `players/[id].tsx`
*   **Responsabilidade**: Rota dinâmica de perfil de jogadores (`/players/{id}`). Instancia a feature `PlayerDetailScreen`.

### `teams/index.tsx`
*   **Responsabilidade**: Rota física da galeria geral de clubes (`/teams`). Instancia a feature `TeamsScreen`.

### `teams/[id].tsx`
*   **Responsabilidade**: Rota dinâmica de perfil de clubes (`/teams/{id}`). Instancia a feature `TeamDetailScreen`.

### `games/index.tsx`
*   **Responsabilidade**: Rota física do histórico e agenda de confrontos (`/games`). Instancia a feature `GamesScreen`.

### `games/[id].tsx`
*   **Responsabilidade**: Rota dinâmica de detalhe de partidas (`/games/{id}`). Instancia a feature `GameDetailScreen`.

### `rankings/index.tsx`
*   **Responsabilidade**: Rota física da classificação geral de líderes (`/rankings`). Instancia a feature `RankingsScreen`.

---

## 7.3 Pasta `src/components/` (UI, Layout e Data)

### `DynamicTable.tsx`
*   **Responsabilidade**: Renderiza grades tabulares genéricas. Realiza formatação decimal e tradução automática de nomes técnicos de colunas para siglas do basquete nacional. Conta com envoltórios de rolagem horizontal com suporte a aceleração física nativa.

### `KeyValueList.tsx`
*   **Responsabilidade**: Componente visual para listagem vertical de informações biográficas ou técnicas rápidas em páginas de detalhes.

### `StatsTable.tsx`
*   **Responsabilidade**: Envolve e filtra dados tabulares brutos, bloqueando a exibição pública de colunas utilitárias internas do SQLite (como `id`, `player_id`, `team_id`).

### `AppShell.tsx`
*   **Responsabilidade**: Contêiner visual unificado. Organiza e renders de forma sequencial vertical o `Header` de controle, a área de conteúdo da tela atual e o rodapé institucional (`Footer`).

### `Header.tsx`
*   **Responsabilidade**: Barra de navegação do sistema. Controla links,Dropdowns na versão web, barra rápida de busca e menu hambúrguer retrátil animado móvel.

### `PageContainer.tsx`
*   **Responsabilidade**: Limitador de área de conteúdo. Centraliza horizontalmente e limita a largura a `1200px` em telas desktop amplas, adicionando margens internas de conforto visual.

### `NavLink.tsx`
*   **Responsabilidade**: Wrapper de navegação inteligente. Compara o caminho atual da rota com a URL do link e aplica realces laranjas caso a rota esteja ativa.

### `Badge.tsx`
*   **Responsabilidade**: Pílula colorida decorativa. Utilizada para categorizar resultados de partidas (`V`/`D`) e posições em rankings gerais.

### `Button.tsx`
*   **Responsabilidade**: Componente de botão estilizado do tema dark. Trata efeitos táteis de clique e exibe spinners internos de carregamento de forma condicional.

### `EmptyState.tsx`
*   **Responsabilidade**: Exibido quando buscas de atletas ou clubes no banco não retornarem correspondências na API, apresentando mensagens ilustrativas de lista vazia.

### `ErrorState.tsx`
*   **Responsabilidade**: Painel de tratamento de falhas de requisição. Oferece explicações visuais amigáveis sobre a falha de conexão com a API e botões de tentativa de reconexão.

### `FallbackImage.tsx`
*   **Responsabilidade**: Trata carregamento de fotos. Caso a foto do jogador ou time venha corrompida ou nula, renderiza círculos coloridos com as iniciais do jogador ou sigla do clube.

### `LoadingState.tsx`
*   **Responsabilidade**: Spinner laranja oficial de aguardo de requisição assíncrona.

### `Select.tsx`
*   **Responsabilidade**: Seletor customizado adaptado para o design system dark. Corrige problemas de interface dos dropdowns nativos do React Native na Web e no Mobile.

### `TextInput.tsx`
*   **Responsabilidade**: Campo estilizado de digitação com suporte a ícones de lupas integrados.

---

## 7.4 Pasta `src/features/` (Estruturas Lógicas das Telas)

### `AskScreen.tsx`
*   **Responsabilidade**: Orquestrador lógico do chat experimental de IA. Gerencia o histórico de perguntas enviadas e direciona respostas assíncronas do uvicorn para os subcomponentes correspondentes.

### `AskInput.tsx`
*   **Responsabilidade**: Caixa de input do chat conversacional. Trata submissões via clique e submissões com a tecla Enter na plataforma Web.

### `AskResult.tsx`
*   **Responsabilidade**: Renderizador dinâmico de tabelas resultantes de buscas bem-sucedidas do `/ask`. Exibe também a explicação textual da pergunta em linguagem natural (`interpreted_as`).

### `AskClarification.tsx`
*   **Responsabilidade**: Exibido quando buscas textuais de IA gerarem resultados ambíguos. Apresenta botões com foto e equipe dos atletas sugeridos para refinar a busca automaticamente.

### `AskExamples.tsx`
*   **Responsabilidade**: Grade com sugestões visuais de perguntas para busca em IA, permitindo ao usuário testar a plataforma rapidamente com um clique.

### `AskStatusMessage.tsx`
*   **Responsabilidade**: Exibe mensagens de feedback e estados de erro de queries não suportadas pela IA.

### `GamesScreen.tsx`
*   **Responsabilidade**: Listagem cronológica de rodadas e partidas disputadas no campeonato.

### `GameDetailScreen.tsx`
*   **Responsabilidade**: Ficha de scouts analíticos da partida. Exibe parciais e estatísticas de posse e aproveitamento de atletas mandantes e visitantes.

### `HomeScreen.tsx`
*   **Responsabilidade**: Dashboard inicial da aplicação. Organiza a classificação resumida, carrosséis de líderes por categorias e o card de jogador de destaque.

### `HighlightCard.tsx`
*   **Responsabilidade**: Calcula e exibe o destaque do dia. Faz a busca da atuação recente de maior eficiência e exibe dados com o jogador de ID `854` como fallback estático padrão.

### `LeaderboardCard.tsx`
*   **Responsabilidade**: Mini-widgets exibindo o Top 1 e corredores secundários de líderes em estatísticas (pontos, assistências, rebotes e eficiência) de uma temporada específica.

### `StandingsWidget.tsx`
*   **Responsabilidade**: Tabela resumida de classificação da temporada em destaque, listando os times ordenados por aproveitamento e vitórias.

### `PlayersScreen.tsx`
*   **Responsabilidade**: Galeria contendo a lista e busca de atletas do NBB, com suporte a paginação.

### `PlayerDetailScreen.tsx`
*   **Responsabilidade**: Perfil do atleta. Mostra dados biográficos, recordes da carreira/temporada, scouts de partidas vigentes e as tabelas verticais bipartidas de médias e totais.

### `PlayerFilters.tsx`
*   **Responsabilidade**: Barra contendo filtros textuais por nome e seletores dinâmicos de equipes.

### `PlayerCard.tsx`
*   **Responsabilidade**: Card básico de atletas para a galeria de jogadores.

### `TeamsScreen.tsx`
*   **Responsabilidade**: Galeria institucional de todos os clubes do campeonato.

### `TeamDetailScreen.tsx`
*   **Responsabilidade**: Perfil de clubes trazendo elenco, títulos, médias e totais agregados por temporada. Remove a coluna `+/-` destas visualizações.

### `TeamCard.tsx`
*   **Responsabilidade**: Card descritivo exibindo escudo e nome de clubes.

### `RankingsScreen.tsx`
*   **Responsabilidade**: Permite filtrar atletas e clubes por temporada e categoria esportiva na tela de rankings de líderes.

### `RankingTable.tsx`
*   **Responsabilidade**: Tabela especializada com realces visuais para o líder de posições.

### `SearchScreen.tsx`
*   **Responsabilidade**: Tela que gerencia as listagens globais de resultados de pesquisas por texto da aplicação.

### `SearchResults.tsx`
*   **Responsabilidade**: Divide e exibe em listas distintas os atletas e times encontrados na pesquisa global.

---

## 7.5 Pasta `src/hooks/` (Compartilhamento de Lógica)

### `useAsync.ts`
*   **Responsabilidade**: Centraliza estados assíncronos do React. Controla flags de carregamento (`loading`), guarda dados resolvidos de sucesso (`data`) e captura erros de rede (`error`).

### `useResponsive.ts`
*   **Responsabilidade**: Hook utilitário. Monitora a largura de tela da janela do navegador web e retorna flags booleanas (`isMobile`, `isTablet`, `isDesktop`) para readequar estilos e ocultar componentes dinamicamente.

---

## 7.6 Pasta `src/theme/` (Design System Dark e Tokens)

### `colors.ts`
*   **Responsabilidade**: Dicionário cromático do sistema. Centraliza as cores oficiais (Laranja NBB `#FF6B00`, fundo do app `#0C0C0E` e cinzas variados).

### `spacing.ts`
*   **Responsabilidade**: Define espaçamentos baseados no grid clássico de basquete (múltiplos de 4px: `4`, `8`, `12`, `16`, `24`, `32`, `48`).

### `typography.ts`
*   **Responsabilidade**: Centraliza famílias de fontes de sistema (`Spline Sans`, `Inter`, etc.) e tamanhos de textos padronizados.

### `index.ts`
*   **Responsabilidade**: Exportador unificado de tema. Disponibiliza a variável `theme` para consumo em arquivos de estilo locais.

---

## 7.7 Pasta `src/types/` (Contratos TypeScript)

### `api.ts`
*   **Responsabilidade**: Tipagens de envelopes genéricos de resposta paginada (`PagedResponse<T>`).

### `ask.ts`
*   **Responsabilidade**: Tipagem para respostas retornadas pelo assistente (/ask), mapeando colunas, linhas e desambiguação de nomes de atletas.

### `models.ts`
*   **Responsabilidade**: Centraliza as tipagens de entidades de negócio do NBB (como `Player`, `Team`, `Game`, `Standing`, `Season`, etc.).

### `declarations.d.ts`
*   **Responsabilidade**: Declara compatibilidade de arquivos `.css` para que importações de estilos não gerem erros no TypeScript.

---

## 7.8 Pasta `src/utils/` (Formatadores e Dicionário de Basquete)

### `errors.ts`
*   **Responsabilidade**: Classe customizada `ApiError` estendendo a classe de erro padrão do JavaScript, encapsulando status e dados das respostas das requisições de rede.

### `formatters.ts`
*   **Responsabilidade**: Converte dados numéricos: `formatDecimal` que trunca estatísticas decimais e `formatPercentage` que transforma aproveitamentos em porcentagens formatadas.

### `labels.ts`
*   **Responsabilidade**: Centraliza o dicionário de siglas esportivas da liga (`labelMap`) e a função `formatColumnLabel` para traduzir cabeçalhos do banco para abreviações oficiais brasileiras.

---

## 7.9 Arquivo de Estilo Estático

### `global.css`
*   **Responsabilidade**: [Suspeito] Arquivo definindo variáveis nativas de fontes (`--font-rounded`, etc.) para navegadores web no Expo Web.

---

# 8. Detalhamento de Regras de Negócio por Componente de Feature

### 8.1 HomeScreen (Dashboard Geral)
O componente `HomeScreen.tsx` renderiza a página inicial. Suas diretrizes técnicas específicas são:
1.  **Destaque do Dia**: Executa uma chamada para listar as partidas e escolhe o jogo de índice `0` (confronto mais recente). Em seguida, escolhe o atleta de maior pontuação de eficiência e exibe-o no card principal.
2.  **Fallback de Destaque**: Caso a API retorne uma lista vazia de partidas (banco SQLite recém-criado), exibe o atleta de ID `854` (Lucas Dias) como destaque padrão.
3.  **Tabela de Classificação**: Renders os times ordenados pela taxa de aproveitamento (`win_pct`) calculada no módulo `data`.

### 8.2 PlayerDetailScreen (Perfil do Atleta)
O componente `PlayerDetailScreen.tsx` gerencia as estatísticas individuais do atleta:
1.  **Jogos da Temporada**: Apenas partidas correspondentes à temporada corrente (`season_id = 18`) são exibidas na tabela de scouts. A coluna de rodadas foi removida para manter a tabela limpa em celulares.
2.  **Tabelas Bipartidas Verticais**: O histórico por temporada do jogador exibe médias decimais e totais inteiros em duas tabelas separadas verticalmente, facilitando a comparação de aproveitamento.
3.  **Ordem de Arremessos**: Arremessos convertidos (makes) são dispostos antes das tentativas (attempts) para consistência visual: `FGM-FGA`, `3PM-3PA`, `2PM-2PA` e `FTM-FTA`.

### 8.3 TeamDetailScreen (Perfil do Clube)
O componente `TeamDetailScreen.tsx` gerencia a página de estatísticas do clube:
1.  **Exclusão do Saldo (+/-)**: O saldo de pontos de quadra (`plus_minus` ou `plus_minus_per_game`) foi completamente omitido das tabelas de médias e totais da página de times.
2.  **Tabelas Bipartidas**: Também divide a visualização histórica por temporada entre médias decimais e totais acumulados dispostos verticalmente.
3.  **Ordem de Arremessos**: Segue o padrão de exibir conversões antes das tentativas (FGM antes de FGA).

### 8.4 RankingsScreen (Líderes de Estatísticas)
O componente `RankingsScreen.tsx` gerencia a listagem comparativa:
1.  **Filtro por Categorias**: Fornece caixas de seleção dinâmicas que disparam requisições buscando o Top 10 de atletas ou times em categorias selecionadas (pontos, assistências, rebotes, turnovers e eficiência).
2.  **Realce de Linha**: A primeira linha (primeiro colocado) é destacada com cor de fundo cinza clara e fonte em negrito.

### 8.5 GameDetailScreen (Ficha de Confrontos)
O componente `GameDetailScreen.tsx` gerencia a visualização de boxscore:
1.  **Ficha Coletiva**: Exibe o placar e as pontuações parciais por quarto de tempo de cada equipe.
2.  **Grades Comparativas**: Apresenta em duas abas ou listas empilhadas as pontuações e estatísticas individuais de cada atleta participante do confronto.

---

# 9. Componentes Complexos do Sistema

### 9.1 DynamicTable (Cálculo de Larguras e Alinhamentos)

O componente `DynamicTable.tsx` adapta-se a variações físicas de telas desktop e mobile:
*   **Larguras Estáticas Customizadas**: Atribui larguras específicas para colunas identificadoras (ex: nomes de jogadores ou times recebem de `150px` a `180px`), mantendo colunas de estatísticas compactas (ex: `60px`).
*   **Alinhamento Dinâmico**: Aplica alinhamento de texto à esquerda (`text-align: left`) para colunas de identificação e centraliza (`text-align: center`) colunas de estatísticas numéricas, facilitando a leitura de tabelas volumosas.
*   **Rolagem Horizontal Independente**: Envolve a tabela com uma tag de rolagem horizontal (`ScrollView horizontal`), garantindo que em smartphones a tela geral não quebre, exibindo uma barra de rolagem local na tabela de dados.

### 9.2 FallbackImage (Iniciais Resilientes)

Como o scraping do campeonato depende de feeds externos de links de fotos que podem vir quebrados ou nulos da API, o componente `FallbackImage.tsx` opera como uma salvaguarda:
*   **Carregamento de Imagem**: Utiliza a biblioteca `Expo Image` para tentar carregar a imagem do link de forma assíncrona.
*   **Lógica de Falha**: Se o carregamento da imagem remota falhar ou a URL for nula, ele intercepta o erro e renderiza um elemento de iniciais estilizado.
*   **Geração de Iniciais**: Remove os sobrenomes e calcula as iniciais (ex: `"Lucas Dias"` vira `"LD"`, `"Franca"` vira `"FRA"`). Desenha um círculo preenchido com a cor de destaque cinza/laranja e exibe as iniciais em caixa alta centralizadas.

---

# 10. Mecanismo do Ask AI (Chat de Linguagem Natural)

O assistente conversacional do DaTabela é baseado em buscas determinísticas controladas que interpretam a intenção do usuário no backend e geram respostas estruturadas no frontend.

### 10.1 Arquitetura de Estados de Resposta

Ao enviar uma pergunta ao backend, o payload de retorno mapeado em `src/types/ask.ts` contém o campo `status`. O frontend lida com os quatro estados de forma especial:

1.  **Status `"ok"`**:
    *   A pergunta foi processada com sucesso.
    *   O painel de chat renderiza o componente `AskResult`.
    *   O resultado exibe a tabela de dados usando o `DynamicTable` e imprime a explicação estruturada do que foi consultado (campo `interpreted_as`).
2.  **Status `"needs_clarification"`**:
    *   Ocorreu ambiguidade (por exemplo, buscar por `"Mateusinho"` quando existem dois atletas cadastrados com essa grafia).
    *   O frontend renderiza o componente `AskClarification` com botões interativos contendo os nomes completos e equipes de cada candidato.
    *   Ao clicar em um candidato, uma nova busca refinada contendo o identificador unívoco é disparada de forma transparente para o usuário.
3.  **Status `"unsupported"`**:
    *   A pergunta digitada foi analisada pela IA, mas o padrão de estatística solicitado não é coberto pelo banco de dados ou pelos templates de consulta vigentes.
    *   O frontend renderiza o componente `AskStatusMessage`, exibindo uma mensagem amigável explicando a limitação e oferecendo sugestões de formatos suportados.
4.  **Status `"error"`**:
    *   Ocorreu falha no processamento interno da rota do servidor.
    *   O frontend exibe uma mensagem de falha técnica genérica de sistema.

### 10.2 Fluxo de Desambiguação (needs_clarification)

O componente `AskClarification.tsx` lê a lista de candidatos (`clarification_candidates`) no JSON retornado pelo backend.
*   Ele desenha botões para cada candidato contendo a foto do atleta (ou fallback), o nome completo e o time atual.
*   A escolha do usuário dispara um novo comando de pesquisa com os parâmetros resolvidos (IDs unívocos), garantindo a precisão das buscas.

---

# 11. Convenções de Desenvolvimento e Padronização

Ao estender ou dar manutenção no código-fonte do frontend, siga as seguintes diretrizes:

*   **Tipagem TypeScript Estrita**: Nunca declare objetos sob a tipagem genérica `any`. Caso novos endpoints sejam disponibilizados, registre as interfaces correspondentes em `src/types/models.ts` ou `src/types/api.ts`.
*   **Espaçamentos e Paletas Centralizadas**: Evite declarar pixels estáticos de margem ou hexadecimais de cor diretamente nos estilos inline. Utilize sempre as variáveis declaradas nos tokens de tema em `colors`, `spacing` e `typography` importados de `../../theme`.
*   **Tratamento de Requisições de Rede**: Chamadas assíncronas do React devem ser processadas por meio do hook `useAsync`. Isso unifica o controle de estados booleanos de carregamento (`loading`) e tratamento de erros de conexão com a API.
*   **Padrão de Nomeação**: Adote nomes descritivos em camelCase para variáveis e PascalCase para declarações de componentes funcionais.

---

# 12. Configuração do Ambiente e API

O frontend comunica-se com a API REST exposta pelo backend FastAPI. Essa comunicação é configurada por meio de variáveis de ambiente.

### 12.1 Criando o arquivo `.env`
Duplique o arquivo `.env.example` na raiz do diretório `frontend/` e renomeie-o para `.env`:
```ini
EXPO_PUBLIC_API_URL=http://127.0.0.1:8000
```

### 12.2 Configuração para Dispositivos Físicos (Expo Go)
Se você for executar a aplicação em um celular físico via aplicativo Expo Go:
1.  O computador e o celular devem estar conectados à **mesma rede Wi-Fi**.
2.  Substitua `127.0.0.1` pelo **IP local** da sua máquina na rede (ex: `192.168.1.50` ou `10.0.0.15`).
3.  O endereço no arquivo `.env` ficará da seguinte forma:
    ```ini
    EXPO_PUBLIC_API_URL=http://192.168.1.50:8000
    ```

---

# 13. Guia de Execução Local

Siga as instruções abaixo para rodar o frontend em ambiente de desenvolvimento local.

### Passo 1: Instalação das dependências
Acesse a pasta `frontend/` no seu console de comandos e execute:
```bash
npm install
```

### Passo 2: Validar o Backend
Certifique-se de que a API do FastAPI está ativa na porta correta (geralmente `8000`).

### Passo 3: Inicializar o Dev Server do Expo

#### Opção A: Executar no Navegador (Expo Web)
Excelente para testar alterações de layout de forma ágil no computador:
```bash
npm run web
```
A página abrirá automaticamente no endereço local `http://localhost:8081`.

#### Opção B: Executar no Celular (Expo Go)
Para rodar no smartphone:
```bash
npm run start
```
Escaneie o QR Code gerado no terminal com a câmera do celular (no iOS) ou com a opção "Scan QR Code" do aplicativo Expo Go (no Android).

---

# 14. Procedimentos de Deploy e Geração de Builds

### 14.1 Compilar para Web (Arquivos Estáticos)
Para compilar uma versão otimizada da aplicação para navegadores de internet:
```bash
npm run build:web
```
Os arquivos otimizados e minimizados serão gravados no diretório `./dist/`. Este diretório pode ser hospedado de forma estática em qualquer servidor HTTP (como Nginx, Apache) ou plataformas modernas de deploy (como Vercel, Netlify, AWS S3).

### 14.2 Compilar para Mobile Nativo (Android / iOS)
A compilação nativa (gerando `.apk`, `.aab` ou `.ipa`) é feita usando o serviço de nuvem oficial do Expo (**EAS Build**):
1.  Instale o utilitário do EAS CLI: `npm install -g eas-cli`
2.  Efetue o login no Expo: `eas login`
3.  Inicie a compilação remota:
    ```bash
    eas build --platform android
    # ou para iOS: eas build --platform ios
    ```

---

# 15. Testes e Checagem Estática de Código

O frontend conta com checagens automáticas de integridade por meio de auditorias do TypeScript Compiler.

### 15.1 Validação de Tipos
Para garantir que não há erros de tipagem, imports inválidos ou referências a arquivos excluídos na base de código, execute:
```bash
npx tsc --noEmit
```
O comando deve retornar sem listar erros de compilação. Recomenda-se rodar este comando antes de enviar alterações de código para o repositório.

### 15.2 Linter de Interface
Para checar a formatação e regras de escrita do código:
```bash
npm run lint
```

---

# 16. Manual de Evolução e Manutenção da Interface

### 16.1 Criando uma Nova Rota (Página)
1.  Adicione o arquivo físico do roteador na pasta correspondente em `src/app/` (ex: criar `src/app/jogadores/comparativo.tsx`).
2.  Desenvolva a interface lógica e os subcomponentes da tela na pasta correspondente em `src/features/` (ex: criar `src/features/players/PlayerCompareScreen.tsx`).
3.  No arquivo criado na pasta `src/app/`, simplesmente importe o componente estruturado da pasta `features/` e exporte-o como padrão.
    ```typescript
    import PlayerCompareScreen from '../../features/players/PlayerCompareScreen';
    export default PlayerCompareScreen;
    ```

### 16.2 Adicionando Novas Siglas Estatísticas
Caso o backend passe a retornar novas colunas estatísticas (como `turnovers_per_game` ou `plus_minus_total`), adicione a chave e sua sigla correspondente no dicionário `labelMap` em `src/utils/labels.ts`:
```typescript
const labelMap: Record<string, string> = {
  // ... siglas existentes
  turnovers_per_game: 'TOV',
  plus_minus_total: '+/- Total',
};
```
O componente `DynamicTable.tsx` irá reconhecer e traduzir o cabeçalho automaticamente na próxima renderização.

---

# 17. Diagnóstico de Problemas Comuns (FAQ)

### 17.1 Erro: `Failed to fetch` ao tentar carregar dados
*   **Causa**: O frontend do Expo não conseguiu se comunicar com a API do backend local.
*   **Resolução**:
    1.  Verifique se a API FastAPI do backend está ativa no terminal.
    2.  Verifique se o arquivo `.env` existe na raiz do frontend e se a variável `EXPO_PUBLIC_API_URL` está apontando para o IP/porta correto da API (ex: `http://127.0.0.1:8000`).
    3.  Se estiver testando no Expo Go no celular, lembre-se que `localhost` ou `127.0.0.1` não funcionam, pois apontariam para o próprio aparelho celular. Use o IP local do seu computador na rede Wi-Fi (ex: `192.168.1.50`).

### 17.2 Erro: `Port 8081 is already in use` ao rodar `npm run web`
*   **Causa**: Outro dev server Metro ou processo está ocupando a porta padrão do Expo Web.
*   **Resolução**: Finalize o processo concorrente ou force o Expo a iniciar em outra porta livre executando:
    ```bash
    npx expo start --port 8082 --web
    ```

### 17.3 Erro de CORS no console do navegador Web
*   **Causa**: O navegador bloqueou a requisição do frontend (porta `8081`) para o backend (porta `8000`) devido a políticas de segurança de mesma origem.
*   **Resolução**: O middleware de CORS no backend FastAPI foi configurado para liberar todas as conexões locais em ambiente de desenvolvimento (`allow_origins=["*"]` em `backend/app/main.py`). Certifique-se de salvar o arquivo no backend e reiniciar o uvicorn.

---

# 18. Auditoria de Arquivos Suspeitos

*   **`src/global.css`**: Este arquivo configura variáveis CSS globais para fontes no Expo Web (como `--font-display`, `--font-mono`). Ele está presente no projeto, mas não é explicitamente importado por nenhum componente TSX em `src/` ou arquivo de layout `_layout.tsx`. Embora não cause erros de compilação ou build, sua remoção deve ser avaliada manualmente caso haja interesse em reestruturar as fontes padrão adotadas no Expo Web.
