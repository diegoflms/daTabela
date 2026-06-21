# DaTabela — Backend

Este README é a documentação principal da pasta `backend/` do **DaTabela**.

Ele explica o papel do backend dentro do projeto, como os CSVs gerados pelo módulo `data/` viram um banco SQLite, como a API FastAPI está organizada, quais endpoints existem, como atualizar a base, como validar o backend, como evoluir rotas e como manter o endpoint experimental `/ask`.

A ideia central é simples:

```text
data gera CSV final
backend importa CSV final para SQLite
backend expõe API FastAPI
frontend consome a API
```

O backend não coleta dados, não faz scraping e não deve corrigir manualmente a base original. Ele é uma camada limpa, testável e recriável de consulta.

---

## Índice

1. [Visão geral do projeto](#1-visão-geral-do-projeto)
2. [Papel de cada área: data, backend e frontend](#2-papel-de-cada-área-data-backend-e-frontend)
3. [Fluxo principal do backend](#3-fluxo-principal-do-backend)
4. [Estado atual do backend](#4-estado-atual-do-backend)
5. [Decisões de arquitetura](#5-decisões-de-arquitetura)
6. [Tabelas finais esperadas](#6-tabelas-finais-esperadas)
7. [Estrutura limpa esperada](#7-estrutura-limpa-esperada)
8. [Mapa completo de arquivos](#8-mapa-completo-de-arquivos)
9. [Instalação e ambiente local](#9-instalação-e-ambiente-local)
10. [Comandos de terminal](#10-comandos-de-terminal)
11. [Rotina operacional](#11-rotina-operacional)
12. [Atualização dos dados](#12-atualização-dos-dados)
13. [Validação e testes](#13-validação-e-testes)
14. [API: endpoints disponíveis](#14-api-endpoints-disponíveis)
15. [Endpoint `/ask`](#15-endpoint-ask)
16. [Como evoluir o backend](#16-como-evoluir-o-backend)
17. [Como investigar erros](#17-como-investigar-erros)
18. [Contrato com o frontend](#18-contrato-com-o-frontend)
19. [Checklist antes de commitar](#19-checklist-antes-de-commitar)
20. [Resumo final](#20-resumo-final)

---

# 1. Visão geral do projeto

O **DaTabela** é um projeto de consulta e exploração de dados históricos da LNB/NBB.

A arquitetura geral pode ser vista assim:

```text
DaTabela/
├── data/
│   └── coleta, limpeza, normalização e geração dos CSVs finais
├── backend/
│   └── importação dos CSVs finais, SQLite, API, busca e /ask
└── frontend/
    └── interface visual que consome os endpoints do backend
```

O backend é responsável por transformar tabelas finais em uma API organizada. Ele não é a fonte original dos dados. A fonte de verdade são os CSVs finais gerados pelo projeto `data`.

---

# 2. Papel de cada área: data, backend e frontend

## 2.1 `data/`

O módulo `data/` é responsável por:

```text
coletar dados
padronizar nomes
resolver aliases
gerar tabelas finais
gerar tabelas derivadas
salvar CSVs finais em data/dados
```

Exemplos de responsabilidades do `data/`:

```text
scraping de jogos
correção de jogadores
correção de times
geração de player_seasons
geração de player_team_seasons
geração de player_career_totals
geração de team_seasons
geração de standings
```

Se um dado estiver errado, o local correto de correção é o `data/`.

---

## 2.2 `backend/`

O backend é responsável por:

```text
ler os CSVs finais do data
recriar o schema SQLite
importar os dados para SQLite
criar índices básicos
expor endpoints estruturados
expor rankings
expor busca
expor /ask
validar se tudo está funcionando
```

O backend pode ser recriado a qualquer momento a partir dos CSVs finais.

---

## 2.3 `frontend/`

O frontend deve consumir a API do backend.

Ele é responsável por:

```text
montar telas
formatar tabelas
escolher colunas visíveis
aplicar destaque visual
lidar com paginação
exibir erros amigáveis
transformar respostas do /ask em componentes
```

Uma decisão importante: quando o `/ask` retorna estatísticas jogo a jogo, o backend entrega a tabela completa. O frontend decide quais colunas mostrar, esconder ou destacar.

---

# 3. Fluxo principal do backend

O fluxo principal é:

```text
DaTabela/data/dados/*.csv
        ↓
python -m scripts.import_csvs
        ↓
database/databela.sqlite3
        ↓
FastAPI
        ↓
rotas estruturadas + rankings + search + /ask
        ↓
frontend
```

Em desenvolvimento, normalmente a API roda em:

```text
http://127.0.0.1:8000
```

A documentação interativa automática fica em:

```text
http://127.0.0.1:8000/docs
```

---

# 4. Estado atual do backend

| Item | Situação |
|---|---|
| API FastAPI | Implementada |
| SQLite local | Implementado |
| Importador CSV para SQLite | Implementado |
| Health checks | Implementados |
| Rotas de temporadas | Implementadas |
| Rotas de times | Implementadas |
| Rotas de jogadores | Implementadas |
| Rotas de jogos | Implementadas |
| Rotas de classificação | Implementadas |
| Rotas de rankings | Implementadas |
| Busca global | Implementada |
| Endpoint `/ask` estilo StatMuse | MVP implementado |
| Scripts operacionais Python | Implementados |
| Testes automatizados | Implementados |
| Integração com frontend | Próximo passo |

---

# 5. Decisões de arquitetura

## 5.1 O `data` é a fonte da verdade

A fonte de verdade do projeto é:

```text
DaTabela/data/dados/*.csv
```

O SQLite é apenas uma cópia otimizada para consulta.

Se algum dado estiver errado, o caminho correto é:

```text
corrigir no data
gerar CSV novamente
reimportar no backend
validar a API
```

Não é recomendado corrigir manualmente o SQLite.

---

## 5.2 O backend importa apenas tabelas finais

O backend deve importar apenas os CSVs finais da raiz de `data/dados`.

Ele não deve depender diretamente de arquivos brutos, temporários, diagnósticos, HTMLs ou arquivos intermediários do pipeline de coleta.

Motivo:

```text
arquivos brutos servem para auditoria
CSVs finais servem para produto
backend deve servir produto
```

---

## 5.3 SQLite é local e recriável

O banco local é gerado a partir dos CSVs.

O banco pode ser apagado e recriado sem perda de informação, desde que os CSVs finais estejam corretos.

---

## 5.4 O schema é derivado dos CSVs

O schema do SQLite é montado a partir dos cabeçalhos dos CSVs finais.

Isso reduz a necessidade de migrations manuais enquanto o projeto ainda pode evoluir.

Consequência:

```text
se uma coluna muda no CSV, endpoints que dependem dela podem precisar de ajuste
```

Por isso o backend deve validar schema e dados depois de importações.

---

## 5.5 O `/ask` é determinístico no MVP

O `/ask` não executa SQL livre gerado por IA.

Ele segue um fluxo seguro:

```text
pergunta
    ↓
normalização
    ↓
detecção de intent
    ↓
resolução de entidade e métrica
    ↓
consulta SQL parametrizada/controlada
    ↓
resposta tabular
```

Esse desenho é mais seguro e mais fácil de testar.

---

## 5.6 Caminho futuro seguro para IA

Se futuramente o `/ask` usar IA, o caminho recomendado é:

```text
pergunta do usuário
        ↓
IA gera plano JSON controlado
        ↓
backend valida o plano
        ↓
backend escolhe template SQL seguro
        ↓
backend executa consulta parametrizada
        ↓
backend retorna tabela
```

Exemplo de plano seguro:

```json
{
  "intent": "player_top_games",
  "players": ["matheusinho"],
  "metric": "points",
  "top_n": 3
}
```

A IA interpreta. O backend valida e executa.

Não é seguro permitir que uma IA gere SQL livre e o backend execute diretamente.

---

# 6. Tabelas finais esperadas

O backend espera encontrar os CSVs finais abaixo em `../data/dados/`:

| CSV | Função |
|---|---|
| `seasons.csv` | Cadastro de temporadas. |
| `teams.csv` | Cadastro de times. |
| `team_aliases.csv` | Nomes alternativos de times. |
| `players.csv` | Cadastro de jogadores. |
| `player_aliases.csv` | Nomes alternativos de jogadores. |
| `games.csv` | Cadastro de jogos. |
| `player_game_stats.csv` | Estatísticas individuais por jogo. |
| `team_game_stats.csv` | Estatísticas dos times por jogo. |
| `standings.csv` | Classificação por temporada. |
| `team_seasons.csv` | Agregados de times por temporada. |
| `player_team_seasons.csv` | Agregados de jogador por time e temporada. |
| `player_seasons.csv` | Agregados de jogador por temporada. |
| `player_career_totals.csv` | Totais históricos de carreira por jogador. |
| `player_records.csv` | Recordes individuais. |
| `awards.csv` | Premiações. |
| `team_titles.csv` | Títulos de times. |

O backend não deve inventar dados que não estejam nessas tabelas.

---

# 7. Estrutura limpa esperada

A estrutura versionada esperada para o backend é:

```text
backend/
├── .gitignore
├── README.md
├── pytest.ini
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── ask_service.py
│   ├── config.py
│   ├── database.py
│   ├── importer.py
│   ├── main.py
│   ├── ranking_service.py
│   ├── repositories.py
│   ├── schema.py
│   ├── search_service.py
│   ├── stat_metrics.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── games.py
│   │   ├── players.py
│   │   ├── stats.py
│   │   ├── table_specs.py
│   │   └── teams.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── ask.py
│   │   ├── games.py
│   │   ├── players.py
│   │   ├── rankings.py
│   │   ├── search.py
│   │   ├── seasons.py
│   │   ├── standings.py
│   │   └── teams.py
│   └── schemas/
│       ├── __init__.py
│       ├── games.py
│       ├── players.py
│       └── teams.py
├── database/
│   └── .gitkeep
├── scripts/
│   ├── __init__.py
│   ├── check_db.py
│   ├── count_rows.py
│   ├── create_schema.py
│   ├── import_csvs.py
│   ├── inspect_schema.py
│   ├── reset_db.py
│   ├── smoke_all.py
│   ├── smoke_ask.py
│   ├── smoke_detail_routes.py
│   ├── smoke_rankings.py
│   ├── smoke_search.py
│   ├── validate_backend.py
│   ├── maintenance/
│   │   ├── __init__.py
│   │   └── cleanup_temp_files.py
│   └── pipeline/
│       ├── __init__.py
│       ├── refresh_backend.py
│       └── update_all.py
└── tests/
    ├── conftest.py
    ├── helpers.py
    ├── test_api_contract.py
    ├── test_api_errors_and_pagination.py
    ├── test_ask.py
    ├── test_basic_routes.py
    ├── test_database.py
    ├── test_database_sanity.py
    ├── test_data_health.py
    ├── test_detail_routes.py
    ├── test_health.py
    ├── test_importer.py
    ├── test_rankings.py
    ├── test_schema.py
    └── test_search.py
```

Arquivos gerados localmente, caches, ambiente virtual, logs e bancos SQLite não fazem parte da estrutura versionada principal.

---

# 8. Mapa completo de arquivos

## 8.1 Raiz do backend

| Arquivo | Função |
|---|---|
| `.gitignore` | Define arquivos locais que não devem ser versionados, como ambiente virtual, caches, logs e bancos gerados. |
| `README.md` | Documentação principal e consolidada do backend. |
| `requirements.txt` | Lista dependências Python necessárias para instalar e executar o backend. |
| `pytest.ini` | Configura o `pytest`, caminhos de importação e opções da suíte de testes. |

---

## 8.2 Pasta `app/`

A pasta `app/` contém a aplicação FastAPI e a lógica principal do backend.

| Arquivo | Função |
|---|---|
| `app/__init__.py` | Marca `app` como pacote Python. |
| `app/main.py` | Cria a aplicação FastAPI, registra routers, define endpoints de sistema e configura CORS para consumo pelo frontend. |
| `app/config.py` | Centraliza configurações de caminho, nome da aplicação, diretório dos dados e banco SQLite. |
| `app/database.py` | Configura SQLAlchemy, engine, sessões e dependência de banco. |
| `app/schema.py` | Monta o schema SQLite com base nos cabeçalhos dos CSVs finais. |
| `app/importer.py` | Lê os CSVs finais e importa as linhas para o SQLite. |
| `app/repositories.py` | Centraliza funções de acesso ao banco, paginação, filtros e consultas reutilizáveis. |
| `app/stat_metrics.py` | Define métricas conhecidas para rankings estruturados. |
| `app/ranking_service.py` | Resolve métricas e monta rankings de jogadores e times. |
| `app/search_service.py` | Implementa busca global e buscas específicas. |
| `app/ask_service.py` | Interpreta perguntas em linguagem natural e executa consultas controladas do `/ask`. |

---

## 8.3 Pasta `app/models/`

A pasta `app/models/` organiza definições de tabelas, entidades e especificações de importação.

| Arquivo | Função |
|---|---|
| `app/models/__init__.py` | Marca a pasta como pacote Python. |
| `app/models/table_specs.py` | Lista tabelas finais esperadas, arquivos CSV correspondentes e colunas importantes para índices. |
| `app/models/games.py` | Estruturas relacionadas a jogos. |
| `app/models/players.py` | Estruturas relacionadas a jogadores. |
| `app/models/teams.py` | Estruturas relacionadas a times. |
| `app/models/stats.py` | Estruturas relacionadas a estatísticas. |

O arquivo mais sensível dessa pasta é `table_specs.py`.

Quando uma nova tabela final entra no backend, normalmente ela precisa ser registrada nele.

---

## 8.4 Pasta `app/schemas/`

A pasta `app/schemas/` guarda schemas de resposta e entrada relacionados às entidades.

| Arquivo | Função |
|---|---|
| `app/schemas/__init__.py` | Marca a pasta como pacote Python. |
| `app/schemas/games.py` | Schemas relacionados a jogos. |
| `app/schemas/players.py` | Schemas relacionados a jogadores. |
| `app/schemas/teams.py` | Schemas relacionados a times. |

Mesmo quando parte dos endpoints retorna dicionários vindos do SQLite, manter schemas é útil para evoluir a API com respostas mais tipadas.

---

## 8.5 Pasta `app/routers/`

Cada arquivo em `app/routers/` expõe um grupo de endpoints.

| Arquivo | Prefixo/área | Função |
|---|---|---|
| `app/routers/__init__.py` | pacote | Marca a pasta como pacote Python. |
| `app/routers/seasons.py` | `/seasons` | Lista temporadas. |
| `app/routers/teams.py` | `/teams` | Lista times, detalhe de time, temporadas e jogos de um time. |
| `app/routers/players.py` | `/players` | Lista jogadores, detalhe, temporadas e jogos de um jogador. |
| `app/routers/games.py` | `/games` | Lista jogos, detalhe, estatísticas individuais e estatísticas de time. |
| `app/routers/standings.py` | `/standings` | Classificação por temporada. |
| `app/routers/rankings.py` | `/rankings` | Rankings estruturados de jogadores e times. |
| `app/routers/search.py` | `/search` | Busca global e buscas específicas. |
| `app/routers/ask.py` | `/ask` | Perguntas em linguagem natural. |

Regra de organização:

```text
router recebe parâmetros
router chama serviço ou repositório
serviço aplica regra de negócio
repositório acessa o banco
```

---

## 8.6 Pasta `database/`

| Arquivo | Função |
|---|---|
| `database/.gitkeep` | Mantém a pasta versionada mesmo sem banco local. |

O banco SQLite gerado fica nessa pasta durante o desenvolvimento, mas deve ser tratado como artefato local recriável.

---

## 8.7 Pasta `scripts/`

Scripts executáveis e utilitários do backend.

| Arquivo | Função |
|---|---|
| `scripts/__init__.py` | Marca `scripts` como pacote Python. |
| `scripts/check_db.py` | Testa conexão básica com o banco. |
| `scripts/create_schema.py` | Cria o schema SQLite a partir dos CSVs finais. |
| `scripts/import_csvs.py` | Importa os CSVs finais para o SQLite. |
| `scripts/inspect_schema.py` | Mostra tabelas e colunas reais do SQLite. |
| `scripts/count_rows.py` | Mostra quantidade de linhas por tabela. |
| `scripts/reset_db.py` | Apoia reset ou recriação do banco. |
| `scripts/validate_backend.py` | Valida se tabelas principais existem e têm dados mínimos. |
| `scripts/smoke_all.py` | Executa smoke test geral dos endpoints principais. |
| `scripts/smoke_ask.py` | Executa smoke test do endpoint `/ask`. |
| `scripts/smoke_detail_routes.py` | Testa rotas de detalhe. |
| `scripts/smoke_rankings.py` | Testa rankings. |
| `scripts/smoke_search.py` | Testa busca. |

---

## 8.8 Pasta `scripts/pipeline/`

Scripts de rotina operacional.

| Arquivo | Função |
|---|---|
| `scripts/pipeline/__init__.py` | Marca a pasta como pacote Python. |
| `scripts/pipeline/refresh_backend.py` | Reimporta e valida o backend em etapas controladas. |
| `scripts/pipeline/update_all.py` | Executa a atualização integrada do projeto de dados e depois chama o refresh do backend. |

---

## 8.9 Pasta `scripts/maintenance/`

Scripts de manutenção local do backend.

| Arquivo | Função |
|---|---|
| `scripts/maintenance/__init__.py` | Marca a pasta como pacote Python. |
| `scripts/maintenance/cleanup_temp_files.py` | Remove temporários locais e, opcionalmente, caches. |

---

## 8.10 Pasta `tests/`

Testes automatizados do backend.

| Arquivo | Função |
|---|---|
| `tests/conftest.py` | Configuração compartilhada dos testes. |
| `tests/helpers.py` | Funções auxiliares para testes. |
| `tests/test_health.py` | Testa endpoints básicos de saúde. |
| `tests/test_database.py` | Testa conexão/configuração do banco. |
| `tests/test_schema.py` | Testa geração de schema. |
| `tests/test_importer.py` | Testa importação CSV para SQLite. |
| `tests/test_data_health.py` | Testa saúde e contagem dos dados. |
| `tests/test_database_sanity.py` | Testa sanidade das tabelas principais. |
| `tests/test_basic_routes.py` | Testa rotas básicas. |
| `tests/test_detail_routes.py` | Testa rotas de detalhe. |
| `tests/test_rankings.py` | Testa rankings. |
| `tests/test_search.py` | Testa busca. |
| `tests/test_ask.py` | Testa `/ask`. |
| `tests/test_api_contract.py` | Testa contrato geral da API. |
| `tests/test_api_errors_and_pagination.py` | Testa erros, limites e paginação. |

---

# 9. Instalação e ambiente local

Na pasta `backend/`:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
```

Para confirmar que o ambiente está ativo:

```powershell
python --version
python -m pip --version
```

Para rodar os testes:

```powershell
python -m pytest
```

Para subir a API:

```powershell
python -m uvicorn app.main:app --reload
```

Depois abra:

```text
http://127.0.0.1:8000/docs
```

---

# 10. Comandos de terminal

Esta seção concentra os comandos principais do backend sem depender de atalhos externos.

## 10.1 Subir a API

```powershell
python -m uvicorn app.main:app --reload
```

Parâmetros úteis:

| Parâmetro | Exemplo | Função |
|---|---|---|
| `--reload` | `python -m uvicorn app.main:app --reload` | Reinicia a API automaticamente ao detectar mudanças no código. |
| `--host` | `python -m uvicorn app.main:app --host 0.0.0.0` | Define o host usado pelo servidor. |
| `--port` | `python -m uvicorn app.main:app --port 8001` | Define a porta usada pelo servidor. |

---

## 10.2 Rodar todos os testes

```powershell
python -m pytest
```

Parâmetros úteis:

| Parâmetro | Exemplo | Função |
|---|---|---|
| `-q` | `python -m pytest -q` | Saída mais curta. |
| `-s` | `python -m pytest -s` | Mostra prints/logs durante os testes. |
| `-k` | `python -m pytest -k ask` | Roda apenas testes cujo nome combina com o termo informado. |
| `--maxfail` | `python -m pytest --maxfail=1` | Para a execução após certo número de falhas. |

---

## 10.3 Reimportar CSVs finais e validar tudo

Use quando os CSVs finais já foram gerados pelo `data/` e você quer atualizar o SQLite do backend.

```powershell
python -m scripts.pipeline.refresh_backend
```

Esse fluxo executa a rotina completa do backend:

```text
importar CSVs
validar tabelas
rodar smoke tests
rodar testes automatizados
```

---

## 10.4 Validar sem reimportar dados

Use quando você alterou apenas código, testes ou documentação e não mexeu nos CSVs finais.

```powershell
python -m scripts.pipeline.refresh_backend --only-checks
```

Parâmetro:

| Parâmetro | Função |
|---|---|
| `--only-checks` | Pula a importação dos CSVs e roda apenas validações, smoke tests e testes. |

---

## 10.5 Atualizar dados e backend no fluxo integrado

Use quando você quer executar o fluxo integrado previsto para atualizar dados e depois backend.

```powershell
python -m scripts.pipeline.update_all
```

Esse comando é o entrypoint integrado do backend. A responsabilidade dele é chamar a atualização do projeto de dados e, em seguida, executar o refresh do backend.

---

## 10.6 Importação manual passo a passo

Quando quiser depurar a importação com mais controle:

```powershell
python -m scripts.import_csvs
python -m scripts.count_rows
python -m scripts.validate_backend
python -m scripts.smoke_all
python -m scripts.smoke_ask
python -m pytest
```

---

## 10.7 Inspecionar banco e schema

```powershell
python -m scripts.check_db
python -m scripts.inspect_schema
python -m scripts.count_rows
```

Use quando aparecer erro do tipo:

```text
no such table
no such column
contagem estranha
tabela vazia
```

---

## 10.8 Resetar ou recriar banco

```powershell
python -m scripts.reset_db
python -m scripts.create_schema
python -m scripts.import_csvs
```

Use com cuidado. O SQLite é recriável, mas a base importada depende dos CSVs finais estarem corretos.

---

## 10.9 Smoke tests específicos

```powershell
python -m scripts.smoke_all
python -m scripts.smoke_ask
python -m scripts.smoke_detail_routes
python -m scripts.smoke_rankings
python -m scripts.smoke_search
```

Use quando quiser validar rapidamente partes específicas da API.

---

## 10.10 Limpeza de temporários

```powershell
python -m scripts.maintenance.cleanup_temp_files
```

Parâmetros:

| Parâmetro | Função |
|---|---|
| `--dry-run` | Mostra o que seria removido sem apagar nada. |
| `--with-cache` | Inclui caches locais na limpeza. |

Exemplos:

```powershell
python -m scripts.maintenance.cleanup_temp_files --dry-run
python -m scripts.maintenance.cleanup_temp_files --with-cache
python -m scripts.maintenance.cleanup_temp_files --dry-run --with-cache
```

---

# 11. Rotina operacional

## 11.1 Quando mudei apenas código do backend

Rode:

```powershell
python -m scripts.pipeline.refresh_backend --only-checks
```

Isso evita reimportar dados sem necessidade.

---

## 11.2 Quando mudei apenas o `/ask`

Rode:

```powershell
python -m scripts.smoke_ask
python -m pytest -k ask
python -m scripts.pipeline.refresh_backend --only-checks
```

Se a mudança no `/ask` exigir coluna nova, tabela nova ou alias novo, corrija primeiro o `data/`, gere os CSVs finais e depois reimporte.

---

## 11.3 Quando mudei uma rota estruturada

Rode:

```powershell
python -m scripts.pipeline.refresh_backend --only-checks
```

Também é recomendado abrir:

```text
http://127.0.0.1:8000/docs
```

e conferir a rota manualmente.

---

## 11.4 Quando mudei CSV final, schema ou importador

Rode:

```powershell
python -m scripts.pipeline.refresh_backend
```

Esse é o caso em que a reimportação é necessária.

---

## 11.5 Quando quero atualizar tudo

O fluxo completo é:

```powershell
cd ..\data
```

Execute a rotina de atualização e geração de derivadas do projeto `data`.

Depois volte para o backend:

```powershell
cd ..\backend
.\.venv\Scripts\activate
python -m scripts.pipeline.refresh_backend
```

O backend começa a partir dos CSVs finais. Então, se o `data/` ainda não gerou os arquivos finais corretamente, o backend não deve tentar corrigir isso sozinho.

---

## 11.6 Logs

O pipeline pode gerar log local em:

```text
logs/last_refresh_backend.log
```

Esse log não substitui a leitura do terminal, mas ajuda a descobrir em qual etapa a rotina falhou.

---

# 12. Atualização dos dados

## 12.1 Regra principal

Sempre que algum CSV final em `data/dados` mudar, o backend precisa ser reimportado.

Exemplos de mudanças que exigem reimportação:

```text
rodar scraping novo
corrigir player_aliases
corrigir players
corrigir games
corrigir player_game_stats
regerar player_seasons
regerar player_team_seasons
regerar player_career_totals
regerar team_seasons
regerar standings
alterar qualquer CSV final
```

---

## 12.2 Mudanças que não exigem reimportação

Não precisa reimportar se você mudou apenas:

```text
README
testes
código do /ask sem mexer nos dados
código de endpoint sem mexer nos dados
frontend
```

Nesses casos, rode:

```powershell
python -m scripts.pipeline.refresh_backend --only-checks
```

---

## 12.3 O que a importação faz

A importação:

```text
lê os cabeçalhos dos CSVs finais
recria o schema do SQLite
apaga dados antigos do SQLite
insere os dados novos
cria índices básicos
```

Por isso é normal o SQLite ser recriado.

---

## 12.4 Posso atualizar com a API ligada?

Em desenvolvimento, até pode.

Mas o recomendado é:

```text
parar API
importar dados
subir API novamente
```

Motivo: durante a importação, as tabelas podem ser recriadas. Se alguém consultar no meio, pode receber erro temporário.

---

## 12.5 Depois de atualizar

Sempre rode:

```powershell
python -m scripts.validate_backend
python -m scripts.smoke_all
python -m scripts.smoke_ask
python -m pytest
```

Depois confira:

```text
http://127.0.0.1:8000/health/data
http://127.0.0.1:8000/docs
```

---

# 13. Validação e testes

## 13.1 Validação mínima saudável

```powershell
python -m scripts.validate_backend
python -m scripts.smoke_all
python -m scripts.smoke_ask
python -m pytest
```

Essa sequência cobre:

```text
sanidade do banco
rotas principais
endpoint /ask
testes automatizados
```

---

## 13.2 Validação após mudar dados ou importação

```powershell
python -m scripts.import_csvs
python -m scripts.validate_backend
python -m scripts.smoke_all
python -m scripts.smoke_ask
python -m pytest
```

---

## 13.3 Validação após mudar apenas `/ask`

```powershell
python -m scripts.smoke_ask
python -m pytest -k ask
```

---

## 13.4 Validação após mudar rankings

```powershell
python -m scripts.smoke_rankings
python -m pytest -k ranking
```

---

## 13.5 Validação após mudar busca

```powershell
python -m scripts.smoke_search
python -m pytest -k search
```

---

# 14. API: endpoints disponíveis

## 14.1 Sistema

| Método | Endpoint | Função |
|---|---|---|
| GET | `/` | Retorna links básicos da API. |
| GET | `/health` | Verifica se a aplicação está rodando. |
| GET | `/health/db` | Verifica se o SQLite está acessível. |
| GET | `/health/schema` | Mostra o catálogo de tabelas finais esperadas. |
| GET | `/health/data` | Mostra a contagem de linhas por tabela no SQLite. |

---

## 14.2 Temporadas

### `GET /seasons`

Lista temporadas.

Parâmetros:

| Parâmetro | Função |
|---|---|
| `limit` | Limita a quantidade de registros retornados. |
| `offset` | Pula uma quantidade inicial de registros para paginação. |

---

## 14.3 Times

### `GET /teams`

Lista times.

Parâmetros:

| Parâmetro | Função |
|---|---|
| `q` | Filtra por termo de busca. |
| `limit` | Limita a quantidade de registros retornados. |
| `offset` | Pula uma quantidade inicial de registros para paginação. |

### `GET /teams/{team_id}`

Retorna detalhe de um time.

### `GET /teams/{team_id}/seasons`

Retorna agregados do time por temporada.

### `GET /teams/{team_id}/games`

Retorna jogos de um time.

Parâmetros:

| Parâmetro | Função |
|---|---|
| `season_id` | Filtra por temporada. |
| `limit` | Limita a quantidade de registros retornados. |
| `offset` | Pula uma quantidade inicial de registros para paginação. |

---

## 14.4 Jogadores

### `GET /players`

Lista jogadores.

Parâmetros:

| Parâmetro | Função |
|---|---|
| `q` | Filtra por termo de busca. |
| `limit` | Limita a quantidade de registros retornados. |
| `offset` | Pula uma quantidade inicial de registros para paginação. |

### `GET /players/{player_id}`

Retorna detalhe de um jogador.

### `GET /players/{player_id}/seasons`

Retorna agregados do jogador por temporada.

### `GET /players/{player_id}/games`

Retorna jogos do jogador.

---

## 14.5 Jogos

### `GET /games`

Lista jogos.

Parâmetros:

| Parâmetro | Função |
|---|---|
| `season_id` | Filtra por temporada. |
| `team_id` | Filtra por time. |
| `limit` | Limita a quantidade de registros retornados. |
| `offset` | Pula uma quantidade inicial de registros para paginação. |

### `GET /games/{game_id}`

Retorna detalhe de um jogo.

### `GET /games/{game_id}/player-stats`

Retorna estatísticas individuais do jogo.

### `GET /games/{game_id}/team-stats`

Retorna estatísticas dos times no jogo.

---

## 14.6 Classificação

### `GET /standings`

Lista classificação por temporada.

Parâmetros:

| Parâmetro | Função |
|---|---|
| `season_id` | Filtra por temporada. |
| `limit` | Limita a quantidade de registros retornados. |
| `offset` | Pula uma quantidade inicial de registros para paginação. |

---

## 14.7 Rankings

### `GET /rankings/players/metrics`

Lista métricas disponíveis para rankings de jogadores.

### `GET /rankings/players/{metric}`

Ranking de jogadores por métrica.

Parâmetros:

| Parâmetro | Função |
|---|---|
| `season_id` | Filtra por temporada. |
| `team_id` | Filtra por time. |
| `min_games` | Define número mínimo de jogos para entrar no ranking. |
| `limit` | Limita a quantidade de registros retornados. |
| `offset` | Pula uma quantidade inicial de registros para paginação. |

### `GET /rankings/teams/metrics`

Lista métricas disponíveis para rankings de times.

### `GET /rankings/teams/{metric}`

Ranking de times por métrica.

Parâmetros:

| Parâmetro | Função |
|---|---|
| `season_id` | Filtra por temporada. |
| `min_games` | Define número mínimo de jogos para entrar no ranking. |
| `limit` | Limita a quantidade de registros retornados. |
| `offset` | Pula uma quantidade inicial de registros para paginação. |

---

## 14.8 Busca

### `GET /search?q=...`

Busca geral em jogadores, times, jogos e temporadas.

### `GET /search/players?q=...`

Busca específica em jogadores.

### `GET /search/teams?q=...`

Busca específica em times.

### `GET /search/games?q=...`

Busca específica em jogos.

Parâmetro principal:

| Parâmetro | Função |
|---|---|
| `q` | Termo textual usado na busca. |

---

## 14.9 Perguntas em linguagem natural

### `GET /ask/examples`

Retorna exemplos suportados pelo `/ask`.

### `GET /ask/intents`

Retorna os tipos de pergunta reconhecidos.

### `POST /ask`

Recebe uma pergunta em linguagem natural.

Exemplo de request:

```json
{
  "question": "matheusinho ultimos 5 jogos"
}
```

Resposta padrão:

```json
{
  "status": "ok",
  "question": "...",
  "title": "...",
  "interpreted_as": {},
  "source_tables": [],
  "columns": [],
  "rows": [],
  "total": 0
}
```

Status possíveis:

```text
ok
not_found
needs_clarification
unsupported
```

---

# 15. Endpoint `/ask`

## 15.1 Ideia

O `/ask` é o começo da funcionalidade estilo StatMuse do DaTabela.

Ele tenta transformar perguntas como:

```text
top 3 jogos com mais pontos do matheusinho
```

em consultas estruturadas sobre o SQLite.

Fluxo:

```text
pergunta
    ↓
normalização de texto
    ↓
identificação de intent
    ↓
resolução de jogador/time/métrica
    ↓
consulta SQL segura
    ↓
resposta tabular
```

---

## 15.2 Resposta esperada

Formato geral:

```json
{
  "status": "ok",
  "question": "...",
  "title": "...",
  "interpreted_as": {},
  "source_tables": [],
  "columns": [],
  "rows": [],
  "total": 0
}
```

---

## 15.3 Status possíveis

| Status | Significado |
|---|---|
| `ok` | A pergunta foi interpretada e executada. |
| `not_found` | A API não encontrou entidade compatível. |
| `needs_clarification` | A API encontrou mais de uma possibilidade e não deve escolher sozinha. |
| `unsupported` | A pergunta ainda não é suportada pelo MVP. |

Exemplo de ambiguidade:

```text
lucas ultimos 5 jogos
```

Se existirem vários jogadores chamados Lucas, o correto é retornar candidatos em vez de escolher arbitrariamente.

---

## 15.4 Intents atuais

| Intent | Exemplo | Fonte correta | Retorno esperado |
|---|---|---|---|
| `player_recent_games` | `matheusinho ultimos 5 jogos` | `player_game_stats` | Últimos N jogos do jogador, com todas as colunas da linha e contexto de jogo/time. |
| `player_top_games` | `top 3 jogos com mais pontos do matheusinho` | `player_game_stats` | Top N jogos do jogador ordenados pela métrica, com `ranking_value`. |
| `players_head_to_head_recent_games` | `matheusinho vs teichmann ultimos 5 jogos` | `player_game_stats` | Últimos N jogos em que os dois jogaram um contra o outro. |
| `ranking` | `top 10 pontos` | `player_career_totals` | Ranking histórico geral de jogadores. |
| `team_history_ranking` | `top 10 times com mais vitorias na historia` | `team_seasons` agregado por `team_id` | Ranking histórico de times. |

---

## 15.5 Regra: perguntas jogo a jogo retornam todas as colunas

Quando a pergunta consulta `player_game_stats`, a API deve retornar todas as colunas disponíveis.

Não deve resumir apenas em:

```text
pontos
rebotes
assistências
```

A resposta deve preservar tudo que existir na linha, como:

```text
minutos
arremessos
rebotes ofensivos
rebotes defensivos
assistências
roubos
tocos
turnovers
faltas
enterradas
plus-minus
eficiência
outras colunas disponíveis
```

Motivo:

```text
backend entrega dados completos
frontend decide apresentação visual
```

---

## 15.6 Regra: `vs` significa confronto direto

Pergunta:

```text
matheusinho vs teichmann ultimos 5 jogos
```

Interpretação correta:

```text
últimos 5 jogos em que os dois jogaram um contra o outro
```

Interpretação errada:

```text
últimos 5 jogos do Matheusinho
+
últimos 5 jogos do Teichmann
```

Regra técnica:

```text
mesmo game_id
dois player_id diferentes
preferencialmente team_id diferente quando team_id existe
```

---

## 15.7 Regra: ranking histórico de jogador usa carreira

Perguntas como:

```text
top 10 pontos
top 10 rebotes
top 10 assistencias
```

sem temporada específica devem usar:

```text
player_career_totals
```

Motivo: ranking geral histórico deve bater com totais de carreira.

Não deve usar `player_seasons`, porque isso retornaria melhores temporadas individuais.

---

## 15.8 Regra: ranking histórico de times agrega temporadas

Pergunta:

```text
top 10 times com mais vitorias na historia
```

Fonte:

```text
team_seasons
```

Regra:

```text
agrupar por team_id
somar métricas por time
ordenar pelo total
```

Não deve retornar melhores temporadas individuais.

---

## 15.9 Como corrigir perguntas quebradas

Quando uma lista de perguntas der problema:

1. Classifique cada pergunta.
2. Veja se é problema de dado ou de interpretação.
3. Se for dado, corrija o projeto `data`.
4. Se for interpretação, corrija `app/ask_service.py`.
5. Adicione testes importantes em `tests/test_ask.py`.
6. Atualize `scripts/smoke_ask.py`.
7. Rode validação.

Comandos:

```powershell
python -m scripts.smoke_ask
python -m pytest -k ask
python -m scripts.pipeline.refresh_backend --only-checks
```

Se a correção exigir coluna nova, tabela nova ou alias novo:

```powershell
python -m scripts.import_csvs
python -m scripts.validate_backend
python -m scripts.smoke_all
python -m scripts.smoke_ask
python -m pytest
```

---

## 15.10 O que pode quebrar ao alterar `/ask`

Pode quebrar:

```text
outras perguntas do /ask
formato de interpreted_as
ordem das colunas
status retornado
testes de /ask
smoke_ask
```

Normalmente não quebra:

```text
rotas /players
rotas /teams
rotas /games
rotas /rankings
importação CSV
SQLite
projeto data
```

Só pode quebrar dados/importação se a pergunta exigir:

```text
nova coluna
nova tabela derivada
mudança de player_aliases
mudança de player_game_stats
mudança de team_seasons
```

Nesse caso, primeiro ajuste o `data`, depois reimporte o backend.

---

# 16. Como evoluir o backend

## 16.1 Ordem segura para mexer

Antes de alterar:

```powershell
python -m pytest
```

Depois de alterar:

```powershell
python -m scripts.smoke_all
python -m scripts.smoke_ask
python -m pytest
```

Se mexeu com dados ou importação:

```powershell
python -m scripts.import_csvs
python -m scripts.validate_backend
python -m scripts.smoke_all
python -m scripts.smoke_ask
python -m pytest
```

---

## 16.2 Nova rota estruturada

Normalmente mexe em:

```text
app/routers/
app/repositories.py
tests/
README.md
```

Checklist:

```text
criar ou alterar router
adicionar função de repositório/serviço se necessário
testar retorno feliz
testar entidade inexistente
testar paginação se aplicável
documentar endpoint neste README
rodar validação
```

---

## 16.3 Nova tabela CSV

Normalmente mexe em:

```text
app/models/table_specs.py
app/schema.py
scripts/import_csvs.py
tests/test_database_sanity.py
README.md
```

Depois rode:

```powershell
python -m scripts.import_csvs
python -m scripts.validate_backend
python -m pytest
```

Se a coluna/tabela não existe no CSV final, o ajuste deve começar no `data/`.

---

## 16.4 Nova pergunta no `/ask`

Normalmente mexe em:

```text
app/ask_service.py
scripts/smoke_ask.py
tests/test_ask.py
README.md
```

Depois rode:

```powershell
python -m scripts.smoke_ask
python -m pytest -k ask
```

---

## 16.5 Nova métrica

Primeiro verifique se a coluna existe no CSV final.

Se a coluna existe:

```text
ajustar aliases em app/ask_service.py
ajustar métricas em app/stat_metrics.py se for usada em /rankings
adicionar teste
rodar validação
```

Se a coluna não existe:

```text
corrigir ou gerar no data
reimportar no backend
ajustar endpoint ou /ask
adicionar teste
```

---

## 16.6 Convenções importantes

```text
data gera CSV
backend importa CSV
SQLite é recriável
/ask não inventa dado
/ask pede clarificação quando a entidade é ambígua
perguntas de jogo de jogador usam player_game_stats
rankings históricos de jogadores usam player_career_totals
rankings históricos de times agregam team_seasons por team_id
consultas com vs significam confronto direto
```

---

# 17. Como investigar erros

## 17.1 Primeiro diagnóstico

Rode:

```powershell
python -m scripts.validate_backend
python -m scripts.smoke_all
python -m scripts.smoke_ask
python -m pytest
```

Depois classifique o erro:

```text
erro de dado
erro de schema
erro de endpoint
erro de interpretação do /ask
erro de teste desatualizado
```

---

## 17.2 Erro de dado

Sintomas:

```text
jogador não encontrado
alias não encontrado
linha faltando
ranking diferente do CSV
contagem estranha
```

Olhar:

```text
DaTabela/data/dados/*.csv
database local gerado
python -m scripts.count_rows
```

Se o dado estiver errado no CSV final, corrija o `data/`.

---

## 17.3 Erro de schema

Sintomas:

```text
no such column
no such table
```

Ações:

```powershell
python -m scripts.import_csvs
python -m scripts.inspect_schema
python -m scripts.validate_backend
```

Causa comum:

```text
CSV mudou coluna
table_specs não foi atualizado
SQLite antigo ainda está em uso
importação falhou antes de terminar
```

---

## 17.4 Erro de endpoint

Sintomas:

```text
404 inesperado
500 em rota específica
paginação errada
filtro ignorado
resposta fora do contrato
```

Olhar:

```text
app/routers/
app/repositories.py
app/ranking_service.py
app/search_service.py
tests/
```

---

## 17.5 Erro do `/ask`

Sintomas:

```text
pergunta cai no intent errado
usa tabela errada
não pede clarificação quando deveria
não acha alias
ordenação do top N errada
ranking histórico usando fonte errada
```

Olhar:

```text
app/ask_service.py
scripts/smoke_ask.py
tests/test_ask.py
```

---

## 17.6 Erro de teste desatualizado

Sintomas:

```text
API funciona manualmente
mas teste espera formato antigo
teste quebra após mudança intencional de contrato
```

Ação:

```text
confirmar se a mudança foi intencional
atualizar teste
atualizar README se o contrato público mudou
rodar suíte completa
```

---

# 18. Contrato com o frontend

## 18.1 Base URL em desenvolvimento

```text
http://127.0.0.1:8000
```

## 18.2 Documentação interativa

```text
http://127.0.0.1:8000/docs
```

## 18.3 Regras para consumo

O frontend deve:

```text
usar paginação quando houver limit/offset
tratar lista vazia como estado válido
tratar status do /ask explicitamente
não assumir que o /ask sempre retorna ok
não depender de ordem de colunas sem conferir columns
exibir erro amigável quando status for unsupported
exibir candidatos quando status for needs_clarification
```

## 18.4 `/ask` no frontend

O frontend deve olhar principalmente:

```text
status
title
interpreted_as
source_tables
columns
rows
total
```

Para perguntas jogo a jogo, o frontend deve decidir visualmente:

```text
colunas fixas
colunas escondidas por padrão
colunas destacadas
ordenação visual
formatação de números
```

O backend deve devolver dados completos e consistentes.

## 18.5 Configuração de CORS (Cross-Origin Resource Sharing)

A aplicação FastAPI configura CORS de forma permissiva para ambiente local em `app/main.py` utilizando o middleware de CORS (`allow_origins=["*"]`). Isso permite que servidores de desenvolvimento Web (como o Metro Bundler do Expo Web na porta `8081`) e emuladores se conectem perfeitamente sem problemas de bloqueio de navegadores.

## 18.6 Ordenação e Relação de Partidas de Jogadores

No endpoint de listagem de jogos por jogador (`/players/{id}/games` resolvido por `list_player_games` em `app/repositories.py`), os jogos são retornados em **ordem cronológica reversa estrita** (`ORDER BY g.game_date DESC, g.game_time DESC, pgs.id DESC`). Isso garante que os jogos mais recentes do atleta sejam listados no topo, simplificando a exibição no frontend e a paginação segura dos dados.

---

# 19. Checklist antes de commitar

## 19.1 Checklist geral

```powershell
python -m scripts.pipeline.refresh_backend --only-checks
```

Confirme:

```text
testes passaram
smoke tests passaram
README está atualizado
estrutura segue o padrão limpo
nenhum banco gerado foi versionado
nenhum cache foi versionado
```

---

## 19.2 Checklist após mudar dados

```powershell
python -m scripts.pipeline.refresh_backend
```

Depois confira:

```text
/health/data
/docs
rankings principais
busca principal
perguntas principais do /ask
```

---

## 19.3 Checklist após mudar contrato de API

```text
teste atualizado
README atualizado
frontend avisado ou ajustado
/docs conferido manualmente
```

---

# 20. Resumo final

O backend do DaTabela é uma camada de consulta sobre os CSVs finais do `data/`.

Resumo mental:

```text
data é a fonte da verdade
backend importa e serve
SQLite é recriável
FastAPI expõe endpoints
frontend decide apresentação
/ask interpreta perguntas de forma controlada
testes e smoke tests protegem o contrato
```

Comandos mais importantes:

```powershell
python -m uvicorn app.main:app --reload
python -m scripts.pipeline.refresh_backend
python -m scripts.pipeline.refresh_backend --only-checks
python -m scripts.smoke_ask
python -m pytest
```

Se houver dúvida entre corrigir no `data` ou no backend, use esta regra:

```text
dado errado ou ausente → corrigir no data
interpretação, rota, contrato ou consulta → corrigir no backend
exibição visual → corrigir no frontend
```
