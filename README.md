# Banco digital: Bootcamp QI Tech 2026

API de um banco digital com cadastro de cliente, conta vinculada, depósito, transferência com tarifa e extrato paginado. Stack: Python 3.11, FastAPI, PostgreSQL 16, Docker e MockServer. Este repositório nasceu do [`bootcamp-base-api`](docs/referencia/base-service-readme.md).

## Rodar e testar

```bash
docker compose up -d                       # api, db e mock (aguarde a api ficar "healthy")
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -v
```

Não é preciso criar `.env`: todo valor tem um padrão no compose. A API responde em `http://localhost:3000`, e toda rota (menos `/` e `/health_check`) exige o header `INTERNAL-TOKEN: default_token`.

Mudou `database/database.sql`? Rode `docker compose down -v`. Mudou `requirements.txt`? Rode `docker compose build --no-cache api`. Há mais detalhes em [rodando localmente](docs/06-operacao/rodando-localmente.md).

## Documentação

Comece pelo **[índice da documentação](docs/README.md)**. Também existe a versão para LLMs em [`llms.txt`](llms.txt).

| Quero entender… | Leia |
|---|---|
| o problema e as garantias sobre o dinheiro | [docs/01-contexto/problema.md](docs/01-contexto/problema.md) |
| regras, restrições R1–R8 e o teste de cada uma | [docs/01-contexto/requisitos.md](docs/01-contexto/requisitos.md) |
| a arquitetura e as camadas | [docs/02-arquitetura/visao-geral.md](docs/02-arquitetura/visao-geral.md) |
| por que cada decisão foi tomada | [docs/02-arquitetura/decisoes/](docs/02-arquitetura/decisoes/README.md) |
| as rotas e os erros | [docs/03-api/rotas.md](docs/03-api/rotas.md), [docs/03-api/erros.md](docs/03-api/erros.md) |
| o modelo de dados | [docs/04-dados/modelo.md](docs/04-dados/modelo.md) |
| a transferência (o principal desafio) | [docs/05-fluxos/transferencia.md](docs/05-fluxos/transferencia.md) |
| como testamos | [docs/07-testes/estrategia.md](docs/07-testes/estrategia.md) |
| como contribuir | [docs/contribuindo.md](docs/contribuindo.md) |
| a RFC da entrega | [docs/rfc/RFC.md](docs/rfc/RFC.md) |

## Estrutura

```
src/        api em camadas: middlewares → schemas → resources → controllers → repositories → models (+ dtos, errors, connectors, utils)
tests/      testes black box por HTTP (integration/) e helpers (utils/)
database/   imagem do Postgres e schema (database.sql)
docs/       documentação navegável; a RFC é derivada dela
```

## Licença

[MIT](LICENSE)
