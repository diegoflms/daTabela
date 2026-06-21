# DaTabela — Documentação da pasta `data/`

Este documento explica a pasta `data/` do **DaTabela** de forma completa: o papel dela dentro do projeto, como os dados públicos da LNB/NBB são transformados em CSVs finais, como os scripts estão organizados, quais arquivos devem ser consumidos pelo backend, quais artefatos são apenas cache/auditoria, como atualizar a base durante uma temporada e como manter o repositório leve no Git.

A ideia central desta pasta é transformar páginas públicas da LNB/NBB em uma base de dados limpa, auditável e pronta para consulta. O `data/` não é a API, não é o frontend e não deve ser confundido com o banco SQLite do backend. Ele é o **pipeline de dados** do projeto.

O fluxo macro do produto é:

```text
data/
    ↓ gera CSVs finais
backend/
    ↓ importa CSVs para SQLite e expõe API
frontend/
    ↓ consome API e apresenta o produto
usuário final
```

O papel específico desta pasta é:

```text
coletar páginas públicas
cachear HTML quando necessário
parsear dados
resolver aliases de times e jogadores
registrar falhas
limpar inconsistências
gerar tabelas derivadas
validar a base
entregar CSVs finais para o backend
```

---

## Índice

1. [Visão geral](#1-visão-geral)
2. [Fonte da verdade](#2-fonte-da-verdade)
3. [Fluxo principal da base](#3-fluxo-principal-da-base)
4. [O que o backend deve consumir](#4-o-que-o-backend-deve-consumir)
5. [Estratégia de versionamento no Git](#5-estratégia-de-versionamento-no-git)
6. [Estrutura limpa recomendada](#6-estrutura-limpa-recomendada)
7. [Mapa dos arquivos da raiz](#7-mapa-dos-arquivos-da-raiz)
8. [Mapa da pasta `dados/`](#8-mapa-da-pasta-dados)
9. [Tabelas finais](#9-tabelas-finais)
10. [Arquivos locais, cache e auditoria](#10-arquivos-locais-cache-e-auditoria)
11. [Scripts de scraping](#11-scripts-de-scraping)
12. [Scripts de build](#12-scripts-de-build)
13. [Scripts de pipeline](#13-scripts-de-pipeline)
14. [Scripts de diagnóstico](#14-scripts-de-diagnóstico)
15. [Scripts de manutenção de boxscores](#15-scripts-de-manutenção-de-boxscores)
16. [Scripts de manutenção de jogadores](#16-scripts-de-manutenção-de-jogadores)
17. [Código-fonte em `src/`](#17-código-fonte-em-src)
18. [Testes](#18-testes)
19. [Como cada tabela é gerada](#19-como-cada-tabela-é-gerada)
20. [O problema dos boxscores](#20-o-problema-dos-boxscores)
21. [O problema dos jogadores](#21-o-problema-dos-jogadores)
22. [Comandos de terminal](#22-comandos-de-terminal)
23. [Parâmetros dos comandos](#23-parâmetros-dos-comandos)
24. [Gerar tudo do zero](#24-gerar-tudo-do-zero)
25. [Rotina diária de atualização](#25-rotina-diária-de-atualização)
26. [Fluxo de nova temporada](#26-fluxo-de-nova-temporada)
27. [Diagnóstico e auditoria](#27-diagnóstico-e-auditoria)
28. [Integração com o backend](#28-integração-com-o-backend)
29. [Checklist antes de commitar](#29-checklist-antes-de-commitar)
30. [Decisões importantes do projeto](#30-decisões-importantes-do-projeto)
31. [Resumo final](#31-resumo-final)

---

# 1. Visão geral

A pasta `data/` é responsável por construir a base estatística do DaTabela.

Ela trabalha com três tipos de material:

```text
1. código do pipeline
2. CSVs finais
3. arquivos locais de execução, cache, diagnóstico e auditoria
```

Os CSVs finais são os arquivos que interessam para o produto. Eles ficam em:

```text
dados/*.csv
```

Os arquivos locais de execução, cache e auditoria podem existir durante o desenvolvimento, mas não precisam ser versionados. Eles incluem HTML bruto, diagnósticos antigos, runtime incremental, amostras de falha e backups de reorganização.

Em termos práticos:

```text
src/      → lógica reutilizável
scripts/  → comandos executáveis
tests/    → testes automatizados
dados/    → CSVs finais e, localmente, caches/auditoria
```

---

# 2. Fonte da verdade

A fonte da verdade do projeto é o conjunto de CSVs finais gerados pelo `data/`.

O backend deve considerar como entrada principal:

```text
DaTabela/data/dados/*.csv
```

O SQLite do backend é uma cópia consultável. Se um dado estiver errado, a correção deve acontecer no `data/`, e não no banco do backend.

Fluxo correto:

```text
corrigir scraping, parser, alias ou tabela manual no data
    ↓
gerar novamente os CSVs finais
    ↓
rodar validações e diagnósticos
    ↓
reimportar no backend
```

Fluxo incorreto:

```text
abrir o SQLite do backend
    ↓
editar valor manualmente
    ↓
achar que corrigiu a fonte
```

Isso é errado porque a próxima importação do backend vai sobrescrever o banco com os CSVs do `data/`.

---

# 3. Fluxo principal da base

O fluxo principal da base é:

```text
dados/seasons.csv
    ↓
scripts.scraping.scrape_teams
    ↓
dados/teams.csv
dados/team_aliases.csv
    ↓
scripts.scraping.scrape_games
    ↓
dados/games.csv
    ↓
scripts.scraping.scrape_players
    ↓
dados/players.csv
dados/player_aliases.csv
    ↓
scripts.scraping.scrape_boxscores
    ↓
dados/player_game_stats.csv
dados/team_game_stats.csv
    ↓
scripts de limpeza, resolução e diagnóstico
    ↓
scripts.pipeline.build_all_derived
    ↓
dados/standings.csv
dados/team_seasons.csv
dados/player_team_seasons.csv
dados/player_seasons.csv
dados/player_career_totals.csv
dados/player_records.csv
```

As tabelas manuais ficam no mesmo conjunto de CSVs finais:

```text
dados/awards.csv
dados/team_titles.csv
```

Essas tabelas são preenchidas manualmente porque alguns dados históricos, prêmios, títulos ou conferências finais podem exigir validação humana.

---

# 4. O que o backend deve consumir

O backend deve consumir apenas os CSVs finais da raiz de `dados/`.

Arquivos que compõem a base final:

```text
dados/seasons.csv
dados/teams.csv
dados/team_aliases.csv
dados/players.csv
dados/player_aliases.csv
dados/games.csv
dados/player_game_stats.csv
dados/team_game_stats.csv
dados/standings.csv
dados/team_seasons.csv
dados/player_team_seasons.csv
dados/player_seasons.csv
dados/player_career_totals.csv
dados/player_records.csv
dados/awards.csv
dados/team_titles.csv
```

O backend não deve depender diretamente de arquivos locais de cache, runtime, diagnóstico ou histórico.

Esses materiais são úteis para manutenção do `data/`, mas não são a base pública do produto.

---

# 5. Estratégia de versionamento no Git

## 5.1 O que eu recomendo versionar

Eu recomendo versionar:

```text
README.md
.gitignore
requirements.txt
pytest.ini
src/
scripts/
tests/
dados/*.csv
```

Ou seja: código, configuração, documentação, testes e CSVs finais.

Motivo: se os CSVs finais forem versionados, outra pessoa consegue clonar o repositório e ter imediatamente a base pronta para o backend importar, sem precisar rodar todo o scraping desde o zero.

Isso é especialmente útil porque scraping pode falhar por vários motivos:

```text
site fora do ar
mudança no HTML
bloqueio temporário
lentidão
boxscore dependente de JavaScript
link antigo quebrado
```

Versionar os CSVs finais dá estabilidade para o backend e para o frontend.

---

## 5.2 O que eu não recomendo versionar

Eu não recomendo versionar:

```text
.venv/
__pycache__/
.pytest_cache/
dados/raw/
dados/_runtime/
dados/diagnostics/
dados/archive/
.reorg_backup/
logs/
estrutura.txt
arquivos de backup
arquivos temporários
```

Motivo: esses arquivos são locais, pesados, ruidosos ou regeneráveis.

Eles atrapalham o Git porque:

```text
pesam o clone
criam diffs enormes
misturam cache com dado oficial
dificultam code review
podem passar de limites do GitHub
podem esconder o que realmente mudou
```

---

## 5.3 E os dados de backup?

Backups não devem ir para o Git.

Se o backup for importante, a melhor opção é guardar fora do repositório, por exemplo:

```text
Google Drive
OneDrive
pasta local fora do repo
release compactada
armazenamento externo
Git LFS, se realmente precisar versionar arquivo grande
```

O Git deve guardar o que é necessário para reconstruir e entender o projeto, não todo o histórico bruto de tentativas.

Em outras palavras:

```text
backup local é segurança operacional
Git é controle de versão do projeto
```

Misturar os dois costuma deixar o repositório pesado e difícil de manter.

---

## 5.4 E os HTMLs brutos?

Os HTMLs brutos são úteis para auditoria e debug, mas não são bons candidatos para Git comum.

Eles podem ser muitos, grandes e mudar com frequência. Além disso, normalmente são regeneráveis pelo scraping ou podem ser mantidos como cache local.

Recomendação:

```text
não versionar dados/raw/
```

Se em algum momento for necessário preservar uma amostra para teste, prefira criar uma pasta pequena e explícita de fixtures, por exemplo:

```text
tests/fixtures/
```

Essa pasta deve ter poucos arquivos, com propósito claro, e não um dump completo de HTML bruto.

---

## 5.5 E os CSVs finais podem pesar?

Podem, mas normalmente pesam muito menos do que HTML bruto e backups.

A regra prática é:

```text
CSV final pequeno/médio → pode versionar
CSV final gigante       → considerar Git LFS ou artifact externo
HTML bruto/cache        → não versionar
backup/archive          → não versionar
```

Se algum CSV final passar de dezenas de MB ou se aproximar do limite do GitHub, use uma destas alternativas:

```text
Git LFS
release compactada
artefato externo
pipeline que baixa a base
separar código e dados em repositórios diferentes
```

Para este projeto, a decisão mais equilibrada é:

```text
versionar somente os CSVs finais da raiz de dados/
ignorar raw, runtime, diagnostics e archive
```

---

# 6. Estrutura limpa recomendada

A estrutura limpa recomendada para o repositório é:

```text
data/
├── .gitignore
├── README.md
├── requirements.txt
├── pytest.ini
├── dados/
│   ├── awards.csv
│   ├── games.csv
│   ├── players.csv
│   ├── player_aliases.csv
│   ├── player_career_totals.csv
│   ├── player_game_stats.csv
│   ├── player_records.csv
│   ├── player_seasons.csv
│   ├── player_team_seasons.csv
│   ├── seasons.csv
│   ├── standings.csv
│   ├── teams.csv
│   ├── team_aliases.csv
│   ├── team_game_stats.csv
│   ├── team_seasons.csv
│   └── team_titles.csv
├── scripts/
│   ├── __init__.py
│   ├── scraping/
│   ├── build/
│   ├── pipeline/
│   ├── diagnostics/
│   └── maintenance/
├── src/
│   ├── __init__.py
│   ├── scraping/
│   ├── transformations/
│   └── utils/
└── tests/
    ├── test_boxscores_parser.py
    ├── test_games_parser.py
    ├── test_players_parser.py
    └── test_standings_parser.py
```

Durante a execução local, outras pastas podem surgir:

```text
dados/raw/
dados/_runtime/
dados/diagnostics/
dados/archive/
.venv/
.pytest_cache/
__pycache__/
```

Essas pastas podem existir no seu computador, mas não precisam entrar no Git.

---

# 7. Mapa dos arquivos da raiz

| Arquivo | Função | Versionar? |
|---|---|---|
| `.gitignore` | Define o que fica fora do Git. Deve manter o repositório leve e impedir cache, ambiente virtual, backup e dados brutos de entrarem no histórico. | Sim |
| `README.md` | Documentação principal da pasta `data/`. Deve explicar o fluxo, comandos, estrutura, decisões e manutenção. | Sim |
| `requirements.txt` | Lista dependências Python necessárias para scraping, parsing, Playwright, testes e manipulação de CSV. | Sim |
| `pytest.ini` | Configura o `pytest`, normalmente ajustando import path e comportamento de testes. | Sim |

Não é necessário manter atalhos de terminal na raiz. O fluxo oficial deve ser executado com `python -m ...`.

---

# 8. Mapa da pasta `dados/`

A pasta `dados/` contém os arquivos finais consumidos pelo backend e, localmente, pode conter arquivos auxiliares gerados durante execução.

## 8.1 Conteúdo versionado recomendado

```text
dados/*.csv
```

Apenas os CSVs finais da raiz.

## 8.2 Conteúdo local recomendado

```text
dados/raw/
dados/_runtime/
dados/diagnostics/
dados/archive/
```

Essas pastas podem existir localmente para auditoria, debug e recuperação de problemas, mas não precisam entrar no Git.

---

# 9. Tabelas finais

## 9.1 `dados/seasons.csv`

Cadastro das temporadas.

Responsabilidades:

```text
definir o ID interno de cada temporada
guardar nome da temporada
guardar slug/código usado no site da LNB
marcar ano inicial e final
indicar qual temporada é atual
```

Essa tabela é a porta de entrada do pipeline. Sem ela, os scrapers não sabem quais temporadas devem consultar.

Cuidados:

```text
manter IDs estáveis
não reutilizar ID antigo
garantir que só uma temporada esteja marcada como atual
validar slugs antes de rodar scraping grande
```

---

## 9.2 `dados/teams.csv`

Cadastro consolidado de times.

Responsabilidades:

```text
guardar times únicos
servir de entidade principal para joins
permitir análise histórica mesmo quando nomes mudam
```

Times podem mudar de nome por patrocínio, cidade, abreviação ou grafia. Por isso, o projeto separa entidade de alias.

---

## 9.3 `dados/team_aliases.csv`

Cadastro de nomes alternativos de times.

Responsabilidades:

```text
resolver nomes crus vindos do site
mapear variações por temporada
evitar criar times duplicados
preservar histórico de nomes
```

Exemplo conceitual:

```text
um mesmo time pode aparecer com nome completo, abreviado ou patrocinado
todos esses nomes devem apontar para o mesmo team_id quando forem a mesma entidade
```

---

## 9.4 `dados/players.csv`

Cadastro consolidado de jogadores.

Responsabilidades:

```text
guardar jogadores únicos
armazenar informações vindas dos perfis
servir de entidade principal para estatísticas
```

Essa tabela é alimentada principalmente pelo scraping dos perfis/listas de jogadores da LNB.

---

## 9.5 `dados/player_aliases.csv`

Cadastro de aliases de jogadores.

Responsabilidades:

```text
resolver nomes crus de boxscore
associar jogador por temporada, time e camisa
reduzir ambiguidade entre nomes parecidos
permitir correções manuais seguras
```

Essa tabela é uma das mais importantes do projeto, porque boxscores podem mostrar jogadores de formas diferentes dos perfis.

---

## 9.6 `dados/games.csv`

Tabela de jogos.

Responsabilidades:

```text
guardar jogo_id
temporada
data
fase
times mandante e visitante
placar
arena
links de origem
status do jogo
```

Essa tabela alimenta standings, estatísticas por time, filtros por temporada e consultas do backend.

---

## 9.7 `dados/player_game_stats.csv`

Tabela de estatísticas individuais por jogador e jogo.

Responsabilidades:

```text
guardar uma linha por jogador em cada jogo
registrar minutos e estatísticas de quadra
permitir consultas de últimos jogos
permitir rankings por jogo
permitir totais e médias derivados
```

É a tabela individual mais importante da base.

Cuidados:

```text
não contar DNP como jogo jogado
não associar jogador sem segurança
não misturar jogador homônimo
manter game_id, team_id e player_id consistentes
```

---

## 9.8 `dados/team_game_stats.csv`

Tabela de estatísticas agregadas de time por jogo.

Responsabilidades:

```text
guardar uma linha por time em cada jogo
registrar estatísticas coletivas
permitir validação contra player_game_stats
servir de base para estatísticas agregadas por temporada
```

Cada jogo completo deve ter, idealmente, duas linhas nessa tabela: uma para cada time.

---

## 9.9 `dados/standings.csv`

Classificação por temporada.

Responsabilidades:

```text
calcular campanha dos times
registrar vitórias e derrotas
permitir classificação por temporada
dar suporte a conferência de campeões e fases finais
```

É derivada principalmente de `games.csv`.

---

## 9.10 `dados/team_seasons.csv`

Estatísticas agregadas por time e temporada.

Responsabilidades:

```text
somar jogos do time na temporada
calcular totais e médias
permitir rankings históricos de times
alimentar endpoints de time por temporada
```

---

## 9.11 `dados/player_team_seasons.csv`

Estatísticas de jogador por time e temporada.

Responsabilidades:

```text
representar a passagem de um jogador por um time em uma temporada
separar trocas de time
permitir análise de produção por equipe
```

Se um jogador atuou por dois times na mesma temporada, ele pode ter duas linhas aqui.

---

## 9.12 `dados/player_seasons.csv`

Estatísticas de jogador por temporada.

Responsabilidades:

```text
agregar a temporada inteira do jogador
somar times quando houve troca de equipe
permitir rankings por temporada independentemente do time
```

Se o jogador passou por mais de um time, esta tabela representa o total da temporada.

---

## 9.13 `dados/player_career_totals.csv`

Totais e médias de carreira.

Responsabilidades:

```text
somar a carreira inteira de cada jogador
calcular médias históricas
alimentar rankings gerais de carreira
```

Para perguntas históricas do tipo “top 10 pontos na história”, esta tende a ser a tabela correta.

---

## 9.14 `dados/player_records.csv`

Recordes individuais.

Responsabilidades:

```text
guardar máximas por jogo
guardar máximas por temporada
guardar marcas relevantes de carreira
facilitar consultas de recordes
```

---

## 9.15 `dados/awards.csv`

Tabela manual de prêmios.

Responsabilidades:

```text
guardar prêmios individuais
corrigir lacunas que scraping não cobre bem
servir de apoio para conteúdo histórico
```

Como é manual, deve ser editada com cuidado e conferência.

---

## 9.16 `dados/team_titles.csv`

Tabela manual ou conferida de títulos.

Responsabilidades:

```text
guardar títulos de times
permitir consultas históricas
complementar standings quando necessário
```

---

# 10. Arquivos locais, cache e auditoria

Esta seção descreve arquivos que podem existir localmente, mas não precisam ser versionados.

## 10.1 `dados/raw/`

Guarda HTML bruto coletado da LNB.

Uso:

```text
auditar origem dos dados
reprocessar parser sem baixar novamente
debugar mudanças de HTML
investigar boxscores quebrados
```

Não recomendo versionar porque pode ficar grande rapidamente.

Subpastas típicas:

```text
dados/raw/boxscores/
dados/raw/games/
dados/raw/players/
dados/raw/player_stats_lists/
dados/raw/standings/
```

---

## 10.2 `dados/_runtime/`

Guarda estado incremental da execução.

Arquivos típicos:

```text
scrape_runs.csv
raw_boxscores.csv
failed_boxscores.csv
failed_player_urls.csv
unresolved_boxscore_players.csv
```

Uso:

```text
saber o que já foi tentado
registrar falhas
rodar apenas pendências
auditar execuções
não repetir trabalho desnecessário
```

Não recomendo versionar por padrão, porque é estado de execução local.

---

## 10.3 `dados/diagnostics/`

Guarda saídas recentes de diagnósticos.

Uso:

```text
listar problemas atuais
conferir inconsistências
apoiar revisão manual
```

Pode ser regenerada. Não precisa entrar no Git.

---

## 10.4 `dados/archive/`

Guarda material antigo, depreciado ou histórico.

Uso:

```text
recuperar arquivos antigos
consultar diagnósticos de fases anteriores
manter amostras antigas de problemas
```

Não recomendo versionar. Se alguma amostra for realmente necessária para teste, mova uma cópia pequena para `tests/fixtures/`.

---

# 11. Scripts de scraping

Os scripts de scraping são os pontos de entrada para coletar informações públicas da LNB/NBB.

## 11.1 `scripts/scraping/scrape_teams.py`

Executa a coleta de times e aliases de times.

Comando:

```powershell
python -m scripts.scraping.scrape_teams
```

Saídas principais:

```text
dados/teams.csv
dados/team_aliases.csv
```

Quando usar:

```text
primeira geração da base
nova temporada
suspeita de time faltando
mudança de nome/patrocinador
```

---

## 11.2 `scripts/scraping/scrape_games.py`

Executa a coleta da tabela de jogos.

Comando:

```powershell
python -m scripts.scraping.scrape_games
```

Saída principal:

```text
dados/games.csv
```

Quando usar:

```text
atualizar calendário
capturar placares novos
corrigir jogos faltantes
atualizar fases e datas
```

---

## 11.3 `scripts/scraping/scrape_players.py`

Executa a coleta de jogadores e aliases de jogadores.

Comando:

```powershell
python -m scripts.scraping.scrape_players --workers 2
```

Saídas principais:

```text
dados/players.csv
dados/player_aliases.csv
dados/_runtime/failed_player_urls.csv
```

Quando usar:

```text
primeira geração da base
nova temporada
novos jogadores no elenco
trocas de time
camisas alteradas
perfis faltando
```

---

## 11.4 `scripts/scraping/scrape_boxscores.py`

Executa a coleta e parsing dos boxscores.

Comando:

```powershell
python -m scripts.scraping.scrape_boxscores --workers 2
```

Saídas principais:

```text
dados/player_game_stats.csv
dados/team_game_stats.csv
dados/raw/boxscores/
dados/_runtime/raw_boxscores.csv
dados/_runtime/failed_boxscores.csv
dados/_runtime/unresolved_boxscore_players.csv
```

Quando usar:

```text
após atualizar jogos
após novos jogos terem boxscore publicado
para reprocessar falhas
para atualizar estatísticas individuais e coletivas
```

Essa é normalmente a etapa mais demorada.

---

# 12. Scripts de build

Os scripts de build geram tabelas derivadas a partir dos CSVs já coletados.

## 12.1 `scripts/build/create_manual_tables.py`

Cria tabelas manuais com cabeçalho.

Comando:

```powershell
python -m scripts.build.create_manual_tables
```

Saídas esperadas:

```text
dados/awards.csv
dados/team_titles.csv
```

Depois da criação, essas tabelas podem exigir preenchimento manual.

---

## 12.2 `scripts/build/build_standings.py`

Gera a classificação por temporada.

Comando:

```powershell
python -m scripts.build.build_standings
```

Saída:

```text
dados/standings.csv
```

---

## 12.3 `scripts/build/build_team_seasons.py`

Gera estatísticas agregadas por time e temporada.

Comando:

```powershell
python -m scripts.build.build_team_seasons
```

Saída:

```text
dados/team_seasons.csv
```

---

## 12.4 `scripts/build/build_player_team_seasons.py`

Gera estatísticas de jogador por time e temporada.

Comando:

```powershell
python -m scripts.build.build_player_team_seasons
```

Saída:

```text
dados/player_team_seasons.csv
```

---

## 12.5 `scripts/build/build_player_seasons.py`

Gera estatísticas de jogador por temporada.

Comando:

```powershell
python -m scripts.build.build_player_seasons
```

Saída:

```text
dados/player_seasons.csv
```

---

## 12.6 `scripts/build/build_player_career_totals.py`

Gera totais e médias de carreira.

Comando:

```powershell
python -m scripts.build.build_player_career_totals
```

Saída:

```text
dados/player_career_totals.csv
```

---

## 12.7 `scripts/build/build_player_records.py`

Gera recordes individuais.

Comando:

```powershell
python -m scripts.build.build_player_records
```

Saída:

```text
dados/player_records.csv
```

---

# 13. Scripts de pipeline

Scripts de pipeline agrupam várias etapas em uma execução só.

## 13.1 `scripts/pipeline/build_all_derived.py`

Executa todos os builders derivados na ordem correta.

Comando:

```powershell
python -m scripts.pipeline.build_all_derived
```

Use quando:

```text
games.csv mudou
player_game_stats.csv mudou
team_game_stats.csv mudou
player_aliases.csv mudou
alguma tabela derivada parece desatualizada
você quer preparar os CSVs finais para o backend
```

Etapas conceituais:

```text
criar/conferir tabelas manuais
gerar standings
gerar team_seasons
gerar player_team_seasons
gerar player_seasons
gerar player_career_totals
gerar player_records
```

---

## 13.2 `scripts/pipeline/update_daily.py`

Executa a rotina diária de atualização.

Comando base:

```powershell
python -m scripts.pipeline.update_daily --workers 2
```

Com jogadores:

```powershell
python -m scripts.pipeline.update_daily --workers 2 --with-players
```

Com renderização de falhas:

```powershell
python -m scripts.pipeline.update_daily --workers 2 --render-failed
```

Uso:

```text
atualizar jogos
tentar boxscores novos
tentar boxscores falhos
rodar limpezas
regenerar derivadas
```

---

# 14. Scripts de diagnóstico

Diagnósticos ajudam a descobrir se a base está saudável.

## 14.1 `scripts/diagnostics/diagnose_boxscores.py`

Comando:

```powershell
python -m scripts.diagnostics.diagnose_boxscores
```

Serve para verificar:

```text
boxscores com falha
jogos sem estatísticas
jogadores não resolvidos
possíveis inconsistências
```

---

## 14.2 `scripts/diagnostics/analyze_failed_boxscores.py`

Comando:

```powershell
python -m scripts.diagnostics.analyze_failed_boxscores
```

Serve para classificar falhas de boxscore e entender se o problema parece ser:

```text
HTML vazio
layout inesperado
página dependente de JavaScript
tabela ausente
erro de parsing
```

---

## 14.3 `scripts/diagnostics/export_boxscore_status.py`

Comando:

```powershell
python -m scripts.diagnostics.export_boxscore_status
```

Serve para exportar um status consolidado de boxscores.

---

## 14.4 `scripts/diagnostics/diagnose_player_team_seasons.py`

Comando:

```powershell
python -m scripts.diagnostics.diagnose_player_team_seasons
```

Serve para conferir se a tabela `player_team_seasons.csv` está coerente com as estatísticas por jogo.

---

## 14.5 `scripts/diagnostics/diagnose_standings.py`

Comando:

```powershell
python -m scripts.diagnostics.diagnose_standings
```

Serve para conferir standings, campanhas e possíveis inconsistências de classificação.

---

# 15. Scripts de manutenção de boxscores

## 15.1 `scripts/maintenance/boxscores/render_failed_boxscores.py`

Usa Playwright para renderizar boxscores que dependem de JavaScript.

Comando:

```powershell
python -m scripts.maintenance.boxscores.render_failed_boxscores --wait-ms 35000
```

Use quando:

```text
requests não enxerga a tabela
a página carrega via JavaScript
diagnóstico mostra falhas recuperáveis
```

Depois de renderizar, reprocessar usando cache:

```powershell
python -m scripts.scraping.scrape_boxscores --only-failed --cache-only --workers 2
```

---

## 15.2 `scripts/maintenance/boxscores/cleanup_team_only_boxscores.py`

Remove falsos sucessos em que há estatística de time, mas não há estatística individual confiável.

Comando:

```powershell
python -m scripts.maintenance.boxscores.cleanup_team_only_boxscores
```

Use quando:

```text
boxscore parece completo, mas só gerou linhas de time
player_game_stats ficou vazio para o jogo
o parser detectou tabela incompleta
```

---

## 15.3 `scripts/maintenance/boxscores/cleanup_dnp_player_game_stats.py`

Remove linhas de jogadores que estavam listados, mas não entraram em quadra.

Comando:

```powershell
python -m scripts.maintenance.boxscores.cleanup_dnp_player_game_stats
```

Use para garantir que DNP não seja contado como jogo jogado.

---

## 15.4 `scripts/maintenance/boxscores/export_failed_boxscore_samples.py`

Exporta amostras de HTML de boxscores com falha.

Comando:

```powershell
python -m scripts.maintenance.boxscores.export_failed_boxscore_samples
```

Use quando precisar montar casos de debug para parser.

---

## 15.5 `scripts/maintenance/boxscores/inspect_boxscore_unknowns.py`

Inspeciona inconsistências entre jogos, estatísticas e falhas.

Comando:

```powershell
python -m scripts.maintenance.boxscores.inspect_boxscore_unknowns
```

---

# 16. Scripts de manutenção de jogadores

## 16.1 `scripts/maintenance/players/suggest_player_resolutions.py`

Sugere resoluções para jogadores não identificados.

Comando:

```powershell
python -m scripts.maintenance.players.suggest_player_resolutions
```

Uso:

```text
analisar nomes crus de boxscore
propor player_id provável
apoiar revisão manual
```

---

## 16.2 `scripts/maintenance/players/resolve_players_by_unique_jersey.py`

Resolve jogadores quando a combinação temporada + time + camisa é única e segura.

Comando:

```powershell
python -m scripts.maintenance.players.resolve_players_by_unique_jersey
```

Uso:

```text
corrigir casos óbvios
reduzir lista de revisão manual
evitar associação insegura por nome solto
```

---

## 16.3 `scripts/maintenance/players/build_player_manual_review.py`

Gera arquivo de revisão manual para jogadores ambíguos.

Comando:

```powershell
python -m scripts.maintenance.players.build_player_manual_review
```

Uso:

```text
separar candidatos que precisam de decisão humana
preparar revisão controlada
evitar chute automático
```

---

## 16.4 `scripts/maintenance/players/apply_player_manual_review.py`

Aplica decisões manuais aprovadas.

Comando:

```powershell
python -m scripts.maintenance.players.apply_player_manual_review
```

Uso:

```text
após revisar candidatos manualmente
quando houver segurança na associação
```

---

## 16.5 `scripts/maintenance/players/apply_player_resolutions.py`

Aplica resoluções revisadas ou automáticas de jogadores.

Comando:

```powershell
python -m scripts.maintenance.players.apply_player_resolutions
```

Uso:

```text
atualizar aliases
reduzir unresolved_boxscore_players
corrigir estatísticas sem player_id
```

---

# 17. Código-fonte em `src/`

A pasta `src/` contém a lógica reutilizável do pipeline.

## 17.1 `src/scraping/`

| Arquivo | Função |
|---|---|
| `src/scraping/http_client.py` | Cliente HTTP compartilhado, responsável por baixar páginas com headers, encoding e tratamento básico. |
| `src/scraping/teams_scraper.py` | Lógica de coleta, consolidação e escrita de times. |
| `src/scraping/games_scraper.py` | Lógica de coleta, consolidação e escrita de jogos. |
| `src/scraping/players_scraper.py` | Lógica de coleta, consolidação e escrita de jogadores. |
| `src/scraping/boxscores_scraper.py` | Lógica de processamento dos boxscores, incluindo cache, falhas, resolução de jogadores e escrita de estatísticas. |

---

## 17.2 `src/scraping/parsers/`

| Arquivo | Função |
|---|---|
| `src/scraping/parsers/teams_parser.py` | Extrai times do HTML da LNB. |
| `src/scraping/parsers/games_parser.py` | Extrai jogos do HTML da LNB. |
| `src/scraping/parsers/players_parser.py` | Extrai dados de jogadores dos perfis da LNB. |
| `src/scraping/parsers/boxscores_parser.py` | Extrai estatísticas individuais e de time dos boxscores. |
| `src/scraping/parsers/standings_parser.py` | Apoia a interpretação de dados usados na classificação. |

---

## 17.3 `src/transformations/`

| Arquivo | Função |
|---|---|
| `src/transformations/stats_helpers.py` | Funções compartilhadas para soma, média, porcentagem e manipulação estatística. |
| `src/transformations/standings_builder.py` | Lógica que gera `standings.csv`. |
| `src/transformations/team_seasons_builder.py` | Lógica que gera `team_seasons.csv`. |
| `src/transformations/player_team_seasons_builder.py` | Lógica que gera `player_team_seasons.csv`. |
| `src/transformations/player_seasons_builder.py` | Lógica que gera `player_seasons.csv`. |
| `src/transformations/player_career_totals_builder.py` | Lógica que gera `player_career_totals.csv`. |
| `src/transformations/player_records_builder.py` | Lógica que gera `player_records.csv`. |

---

## 17.4 `src/utils/`

| Arquivo | Função |
|---|---|
| `src/utils/csv_io.py` | Funções para ler, criar, escrever e substituir CSVs com segurança. |
| `src/utils/text.py` | Funções de limpeza de texto, normalização, slug, remoção de acentos e extração de partes de URL. |

---

# 18. Testes

A pasta `tests/` valida parsers e transformações importantes.

| Arquivo | Função |
|---|---|
| `tests/test_boxscores_parser.py` | Testa parsing dos boxscores. |
| `tests/test_games_parser.py` | Testa parsing das páginas de jogos. |
| `tests/test_players_parser.py` | Testa parsing dos perfis de jogadores. |
| `tests/test_standings_parser.py` | Testa parsing ou construção relacionada à classificação. |

Comando:

```powershell
python -m pytest
```

---

# 19. Como cada tabela é gerada

## 19.1 Ordem segura

Ordem segura para gerar a base:

```text
1. Conferir seasons.csv
2. Gerar teams.csv e team_aliases.csv
3. Gerar games.csv
4. Gerar players.csv e player_aliases.csv
5. Gerar player_game_stats.csv e team_game_stats.csv
6. Rodar limpezas de boxscore
7. Resolver jogadores ambíguos
8. Criar/conferir tabelas manuais
9. Gerar derivadas
10. Rodar diagnósticos
11. Rodar testes
```

---

## 19.2 Dependências entre tabelas

```text
seasons.csv
    → scrape_teams
    → scrape_games
    → scrape_players
    → scrape_boxscores
```

```text
games.csv
player_game_stats.csv
team_game_stats.csv
    → standings.csv
    → team_seasons.csv
    → player_team_seasons.csv
    → player_seasons.csv
    → player_career_totals.csv
    → player_records.csv
```

```text
players.csv
player_aliases.csv
    → resolução de jogadores nos boxscores
    → player_game_stats.csv confiável
```

```text
teams.csv
team_aliases.csv
    → resolução de times em jogos e boxscores
    → standings e team_seasons confiáveis
```

---

# 20. O problema dos boxscores

Boxscore foi uma das partes mais difíceis porque a LNB/NBB não necessariamente apresenta todos os jogos no mesmo formato.

Problemas comuns:

```text
boxscore sem tabela útil
boxscore com layout clássico
boxscore com layout realtime
boxscore dependente de JavaScript
boxscore com jogadores listados sem terem jogado
boxscore com estatística de time mas sem estatística individual
boxscore com nomes de jogadores difíceis de resolver
```

Por isso o projeto adota uma postura conservadora:

```text
não marcar como sucesso quando o dado é parcial demais
não associar jogador por chute
não contar DNP como jogo
não apagar falhas sem registrar
```

A regra principal é:

```text
melhor incompleto e auditável do que completo e errado
```

---

## 20.1 Boxscore clássico

Modelo em que a tabela de estatísticas já aparece de forma relativamente direta no HTML.

Normalmente é tratado pelo parser comum.

---

## 20.2 Boxscore realtime

Modelo em que a estrutura da página ou dos dados é diferente, exigindo tratamento específico.

O parser precisa reconhecer esse formato para não classificar como tabela desconhecida.

---

## 20.3 Boxscore dependente de JavaScript

Modelo em que o HTML obtido por `requests` pode vir vazio ou incompleto, porque a tabela aparece depois da execução de JavaScript no navegador.

Nesses casos, use Playwright:

```powershell
python -m scripts.maintenance.boxscores.render_failed_boxscores --wait-ms 35000
python -m scripts.scraping.scrape_boxscores --only-failed --cache-only --workers 2
```

---

# 21. O problema dos jogadores

Jogadores são difíceis por vários motivos:

```text
nomes abreviados
nomes com acentos
nomes iguais ou parecidos
apelidos
mudança de time
mudança de camisa
jogadores estrangeiros com grafias diferentes
boxscore sem link direto confiável
```

Por isso o projeto usa `player_aliases.csv`.

Uma associação segura pode usar:

```text
temporada
time
camisa
nome cru no boxscore
nome do perfil
player_id existente
histórico do jogador
```

Evite resolver jogador apenas por nome quando houver ambiguidade.

---

# 22. Comandos de terminal

Todos os comandos abaixo devem ser executados a partir da raiz da pasta `data/`.

## 22.1 Preparar ambiente

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## 22.2 Rodar testes

```powershell
python -m pytest
```

## 22.3 Scraping de times

```powershell
python -m scripts.scraping.scrape_teams
```

## 22.4 Scraping de jogos

```powershell
python -m scripts.scraping.scrape_games
```

## 22.5 Scraping de jogadores

```powershell
python -m scripts.scraping.scrape_players --workers 2
```

## 22.6 Scraping de boxscores

```powershell
python -m scripts.scraping.scrape_boxscores --workers 2
```

## 22.7 Renderizar boxscores falhos com Playwright

```powershell
python -m scripts.maintenance.boxscores.render_failed_boxscores --wait-ms 35000
```

## 22.8 Reprocessar apenas boxscores falhos usando cache

```powershell
python -m scripts.scraping.scrape_boxscores --only-failed --cache-only --workers 2
```

## 22.9 Limpezas de boxscore

```powershell
python -m scripts.maintenance.boxscores.cleanup_team_only_boxscores
python -m scripts.maintenance.boxscores.cleanup_dnp_player_game_stats
```

## 22.10 Resolução de jogadores

```powershell
python -m scripts.maintenance.players.suggest_player_resolutions
python -m scripts.maintenance.players.resolve_players_by_unique_jersey
python -m scripts.maintenance.players.build_player_manual_review
python -m scripts.maintenance.players.apply_player_manual_review
python -m scripts.maintenance.players.apply_player_resolutions
```

## 22.11 Criar tabelas manuais

```powershell
python -m scripts.build.create_manual_tables
```

## 22.12 Gerar todas as derivadas

```powershell
python -m scripts.pipeline.build_all_derived
```

## 22.13 Rodar diagnósticos principais

```powershell
python -m scripts.diagnostics.diagnose_boxscores
python -m scripts.diagnostics.diagnose_player_team_seasons
python -m scripts.diagnostics.diagnose_standings
```

## 22.14 Rotina diária

```powershell
python -m scripts.pipeline.update_daily --workers 2
```

## 22.15 Rotina diária incluindo jogadores

```powershell
python -m scripts.pipeline.update_daily --workers 2 --with-players
```

## 22.16 Rotina diária tentando renderizar falhas

```powershell
python -m scripts.pipeline.update_daily --workers 2 --render-failed
```

---

# 23. Parâmetros dos comandos

Os parâmetros documentados no fluxo atual são:

| Parâmetro | Usado em | Função |
|---|---|---|
| `--workers N` | `scrape_players`, `scrape_boxscores`, `update_daily` | Define quantidade de workers/processos/execuções paralelas. Use valores baixos, como `2`, para evitar sobrecarregar o site e reduzir chance de falha. |
| `--wait-ms N` | `render_failed_boxscores` | Define quanto tempo o Playwright espera, em milissegundos, para a página carregar antes de salvar o HTML renderizado. |
| `--only-failed` | `scrape_boxscores` | Reprocessa apenas jogos que estão na lista de falhas. Útil para recuperação incremental. |
| `--cache-only` | `scrape_boxscores` | Usa HTML já salvo localmente em vez de baixar de novo. Útil depois de renderizar falhas com Playwright. |
| `--with-players` | `update_daily` | Inclui atualização de jogadores na rotina diária. Não precisa rodar todo dia, mas é útil periodicamente. |
| `--render-failed` | `update_daily` | Tenta renderizar boxscores falhos com Playwright durante a rotina de atualização. |

Valores recomendados no uso comum:

```text
--workers 2
--wait-ms 35000
```

Observação: se a internet estiver instável ou o site estiver respondendo lentamente, diminua o paralelismo. Para scraping, estabilidade geralmente vale mais que velocidade.

---

# 24. Gerar tudo do zero

Use este fluxo quando estiver montando a base em uma máquina nova ou quando quiser reconstruir tudo.

## 24.1 Preparar ambiente

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## 24.2 Conferir temporadas

Edite manualmente:

```text
dados/seasons.csv
```

Garanta:

```text
temporadas cadastradas
slugs corretos
IDs estáveis
uma única temporada atual
```

## 24.3 Rodar scraping base

```powershell
python -m scripts.scraping.scrape_teams
python -m scripts.scraping.scrape_games
python -m scripts.scraping.scrape_players --workers 2
python -m scripts.scraping.scrape_boxscores --workers 2
```

## 24.4 Recuperar falhas de boxscore quando necessário

```powershell
python -m scripts.maintenance.boxscores.render_failed_boxscores --wait-ms 35000
python -m scripts.scraping.scrape_boxscores --only-failed --cache-only --workers 2
```

## 24.5 Rodar limpezas

```powershell
python -m scripts.maintenance.boxscores.cleanup_team_only_boxscores
python -m scripts.maintenance.boxscores.cleanup_dnp_player_game_stats
```

## 24.6 Resolver jogadores

```powershell
python -m scripts.maintenance.players.suggest_player_resolutions
python -m scripts.maintenance.players.resolve_players_by_unique_jersey
python -m scripts.maintenance.players.build_player_manual_review
python -m scripts.maintenance.players.apply_player_manual_review
python -m scripts.maintenance.players.apply_player_resolutions
```

## 24.7 Criar/conferir tabelas manuais

```powershell
python -m scripts.build.create_manual_tables
```

Depois confira manualmente:

```text
dados/awards.csv
dados/team_titles.csv
```

## 24.8 Gerar derivadas

```powershell
python -m scripts.pipeline.build_all_derived
```

## 24.9 Diagnosticar

```powershell
python -m scripts.diagnostics.diagnose_boxscores
python -m scripts.diagnostics.diagnose_player_team_seasons
python -m scripts.diagnostics.diagnose_standings
python -m pytest
```

---

# 25. Rotina diária de atualização

Durante temporada em andamento, a rotina comum é:

```powershell
python -m scripts.pipeline.update_daily --workers 2
```

Essa rotina deve atualizar jogos, tentar boxscores novos/falhos, rodar limpezas e regenerar derivadas.

Use em dias com jogos ou no dia seguinte.

Motivo:

```text
novos placares mudam standings
novos boxscores mudam estatísticas individuais
rankings e médias mudam
backend precisa dos CSVs finais atualizados
```

---

## 25.1 Atualização com jogadores

Uma ou duas vezes por semana:

```powershell
python -m scripts.pipeline.update_daily --workers 2 --with-players
```

Use quando:

```text
jogadores novos aparecem
elencos mudam
camisas mudam
aliases precisam ser atualizados
trocas de time afetam estatísticas
```

---

## 25.2 Atualização com renderização de falhas

Quando os diagnósticos mostrarem muitas falhas recuperáveis:

```powershell
python -m scripts.pipeline.update_daily --workers 2 --render-failed
```

Use quando:

```text
boxscores dependem de JavaScript
requests não capturou a tabela
o cache renderizado pode resolver falhas
```

---

# 26. Fluxo de nova temporada

Quando uma nova temporada começar:

1. Editar `dados/seasons.csv`.
2. Marcar a temporada anterior como não atual.
3. Adicionar a nova temporada.
4. Conferir slug/código da LNB.
5. Rodar scraping de times.
6. Rodar scraping de jogos.
7. Rodar scraping de jogadores.
8. Rodar rotina diária com jogadores.
9. Conferir diagnósticos.
10. Revisar jogadores não resolvidos.
11. Gerar derivadas.
12. Reimportar no backend.

Comandos principais:

```powershell
python -m scripts.scraping.scrape_teams
python -m scripts.scraping.scrape_games
python -m scripts.scraping.scrape_players --workers 2
python -m scripts.pipeline.update_daily --workers 2 --with-players
python -m scripts.pipeline.build_all_derived
python -m scripts.diagnostics.diagnose_boxscores
python -m scripts.diagnostics.diagnose_standings
python -m scripts.diagnostics.diagnose_player_team_seasons
python -m pytest
```

Atenção: nova temporada costuma revelar problemas novos, porque times mudam de nome, jogadores trocam de equipe, camisas mudam e o site pode alterar a estrutura de páginas.

---

# 27. Diagnóstico e auditoria

## 27.1 Como achar problema em jogador

Confira:

```text
dados/players.csv
dados/player_aliases.csv
dados/_runtime/unresolved_boxscore_players.csv
dados/player_game_stats.csv
HTML do boxscore em dados/raw/
```

Perguntas importantes:

```text
o jogador existe em players.csv?
o alias existe em player_aliases.csv?
a temporada está correta?
o time está correto?
a camisa bate?
o nome cru é ambíguo?
há mais de um jogador possível?
```

---

## 27.2 Como achar problema em boxscore

Confira:

```text
dados/games.csv
dados/player_game_stats.csv
dados/team_game_stats.csv
dados/_runtime/failed_boxscores.csv
dados/raw/boxscores/game_<id>.html
```

Perguntas importantes:

```text
o jogo existe em games.csv?
o boxscore foi baixado?
o HTML tem tabela?
a tabela depende de JavaScript?
o parser reconhece o layout?
há estatística de time mas não de jogador?
há jogadores não resolvidos?
```

---

## 27.3 Como achar problema em time

Confira:

```text
dados/teams.csv
dados/team_aliases.csv
dados/games.csv
dados/team_game_stats.csv
dados/team_seasons.csv
dados/standings.csv
```

Perguntas importantes:

```text
o time foi criado duplicado?
o alias está correto?
o mesmo time mudou de nome?
o team_id está consistente?
a temporada está correta?
```

---

## 27.4 Como achar problema em tabela derivada

Confira primeiro as tabelas de origem.

Exemplos:

```text
standings.csv depende de games.csv
team_seasons.csv depende de games.csv e team_game_stats.csv
player_team_seasons.csv depende de player_game_stats.csv
player_seasons.csv depende de player_team_seasons.csv
player_career_totals.csv depende de player_seasons.csv
player_records.csv depende de player_game_stats.csv e agregações
```

Se uma derivada está errada, a causa pode estar:

```text
na tabela de origem
no builder
em uma coluna ausente
em um alias errado
em um jogador sem player_id
em um jogo duplicado ou incompleto
```

---

# 28. Integração com o backend

Depois de atualizar o `data/`, o backend precisa reimportar os CSVs.

Fluxo recomendado a partir da raiz do projeto maior:

```powershell
cd data
.\.venv\Scripts\activate
python -m scripts.pipeline.update_daily --workers 2
python -m scripts.pipeline.build_all_derived
python -m pytest

cd ..\backend
.\.venv\Scripts\activate
python -m scripts.pipeline.refresh_backend
```

Se você alterou apenas o `data/`, o backend não precisa ser alterado no código, mas precisa reimportar os CSVs finais.

O backend deve consumir:

```text
DaTabela/data/dados/*.csv
```

Não deve depender de:

```text
dados/raw/
dados/_runtime/
dados/diagnostics/
dados/archive/
```

---

# 29. Checklist antes de commitar

Antes de commitar código ou CSV final:

```powershell
python -m scripts.pipeline.build_all_derived
python -m scripts.diagnostics.diagnose_boxscores
python -m scripts.diagnostics.diagnose_player_team_seasons
python -m scripts.diagnostics.diagnose_standings
python -m pytest
```

Conferir manualmente:

```text
dados/seasons.csv
dados/teams.csv
dados/team_aliases.csv
dados/players.csv
dados/player_aliases.csv
dados/games.csv
dados/player_game_stats.csv
dados/team_game_stats.csv
dados/standings.csv
dados/team_seasons.csv
dados/player_team_seasons.csv
dados/player_seasons.csv
dados/player_career_totals.csv
dados/player_records.csv
dados/awards.csv
dados/team_titles.csv
```

Não commitar:

```text
ambiente virtual
cache Python
cache de pytest
HTML bruto
diagnósticos gerados
runtime incremental
backups
arquivos temporários
```

---

# 30. Decisões importantes do projeto

## 30.1 Separar entidade de alias

Times e jogadores podem aparecer com nomes diferentes ao longo do tempo.

Por isso existem:

```text
teams.csv
team_aliases.csv
players.csv
player_aliases.csv
```

A entidade representa “quem é”. O alias representa “como apareceu em determinada fonte/contexto”.

---

## 30.2 Manter falhas visíveis

O projeto não tenta esconder falhas.

Falhas são registradas para que possam ser corrigidas depois.

Isso é melhor do que fingir que a base está completa quando alguns jogos ou jogadores ainda precisam de revisão.

---

## 30.3 Não forçar associação insegura

Se um jogador não puder ser associado com segurança, ele deve ficar pendente.

Associação errada é pior do que dado ausente, porque contamina rankings, médias e histórico.

---

## 30.4 Não contar DNP como jogo

Jogador listado mas que não entrou em quadra não deve ser tratado como jogador com partida disputada.

Isso evita inflar jogos, médias e totais.

---

## 30.5 Cache local é útil, mas não precisa ir para Git

HTML bruto e arquivos de runtime são úteis para debug local.

Mas o Git deve priorizar:

```text
código
documentação
testes
CSVs finais
```

---

## 30.6 O backend não corrige dado

O backend importa e serve dados.

A correção de dado deve acontecer aqui no `data/`.

---

# 31. Resumo final

A pasta `data/` é a fundação do DaTabela.

Ela transforma dados públicos da LNB/NBB em CSVs finais organizados, consistentes e prontos para o backend.

O fluxo essencial é:

```text
seasons
    ↓
times
    ↓
jogos
    ↓
jogadores
    ↓
boxscores
    ↓
limpeza e resolução
    ↓
derivadas
    ↓
diagnóstico
    ↓
backend
```

A regra de ouro é:

```text
CSV final na raiz de dados/ é produto
raw/runtime/diagnostics/archive é suporte local
```

A segunda regra de ouro é:

```text
é melhor deixar um problema explícito do que esconder uma associação errada
```

Com isso, qualquer pessoa consegue entender:

```text
de onde veio cada dado
qual script gerou cada tabela
qual tabela alimenta o backend
qual etapa falhou
qual problema ainda precisa de revisão
como atualizar a base
como manter o Git leve
```
