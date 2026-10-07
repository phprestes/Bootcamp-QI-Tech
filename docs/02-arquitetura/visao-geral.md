---
title: Visão geral da arquitetura
summary: O ecossistema (api, db, mock do birô), quem chama quem, e como uma requisição atravessa as camadas.
related: [camadas.md, decisoes/0001-monolito-com-mock-externo.md, ../06-operacao/rodando-localmente.md]
sources: [Aula 2 p.6-12 (ecossistema na RFC), Aula 3 manhã p.30-33, Aula 3 tarde p.21-25, Dia 4 manhã notas 22 e 31-35]
---

# Visão geral

> [Índice](../README.md) › Arquitetura › Visão geral
>
> **Responde a:** quais serviços sobem? quem fala com quem? o que é stateless?

## Ecossistema

São três containers num único `docker-compose.yml`. A decisão está em [ADR 0001](decisoes/0001-monolito-com-mock-externo.md).

```mermaid
flowchart LR
    caller["Sistema interno<br/>(ou pytest)"] -- "HTTP + INTERNAL-TOKEN" --> api
    subgraph compose["docker compose"]
        api["api<br/>FastAPI · :3000"] -- "SQLAlchemy" --> db[("db<br/>PostgreSQL 16")]
        api -- "HTTP, timeout 5s<br/>BUREAU_API_URL" --> mock["mock<br/>MockServer · :1080<br/>(papel do birô de CPF)"]
    end
    pytest["pytest"] -. "expectation / verify" .-> mock
```

| Serviço | Imagem | Papel | Saúde |
|---|---|---|---|
| `api` | build local (`Dockerfile`) | Regras de cliente, conta e transação | `GET /health_check` a cada 3s |
| `db` | build de `database/` (postgres:16 + `database.sql` em initdb) | Fonte da verdade do saldo e do histórico | `pg_isready` |
| `mock` | `mockserver/mockserver:mockserver-5.11.1` | Finge ser o birô. Sobe vazio, e cada teste ensina a resposta | — |

**Em produção** (fora do escopo, mas é a resposta que a banca espera):

- O `mock` dá lugar ao birô real e a API fica atrás de um API Gateway, a única porta pública.
- Rodam N réplicas da API atrás de um load balancer, que usa o `/health_check`.
- O auto scaling é guiado por métricas (p95 e taxa de 5xx). Escalar a API **não** escala o banco: cada réplica abre o próprio pool de conexões.

## A API é stateless

A sessão de banco nasce e morre em cada requisição, no middleware `session_manager`, e nada fica guardado em memória entre pedidos. Por isso qualquer réplica pode atender qualquer requisição. Toda informação de estado mora no Postgres.

## Caminho de uma requisição

```mermaid
flowchart LR
    A[app.py] --> M[middlewares<br/>request_context → request_logger → internal_token → session_manager]
    M --> S[schemas<br/>JSON Schema]
    S --> R[resources<br/>HTTP in/out]
    R --> C[controllers<br/>regra + commit]
    C --> RP[repositories<br/>SQL]
    RP --> MD[models] --> DB[(database.sql)]
    C --> CN[connectors<br/>birô] --> EXT[serviço de fora]
    C --> D[dtos<br/>saída]
```

A seta anda num sentido só: `resources → controllers → repositories → models`. O controller também chama `connectors`. O detalhe de cada pasta está em [camadas](camadas.md).

## Recursos do domínio

| Recurso | Pai | Responsável |
|---|---|---|
| `customer` | — | `CustomerController` + `BureauConnector` |
| `account` | `customer` | `AccountController` |
| `transaction` | `account` | `TransactionController` |
