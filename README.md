# Banco digital: Bootcamp QI Tech 2026

API de um banco digital com cadastro de cliente, conta vinculada, depósito, transferência com tarifa e extrato paginado. Stack: Python 3.11, FastAPI, PostgreSQL 16, Docker e MockServer. Este repositório nasceu do [`bootcamp-base-api`](docs/referencia/base-service-readme.md).

## Rodar e testar

```bash
make all      # sobe api, db e mock, espera ficarem healthy, cria o .venv (Python 3.11) e roda o pytest
```

`make` sem argumento lista todos os alvos (`up`, `test`, `lint`, `reset`, `rebuild`, `logs`, `clean`…). O `make install` usa `python3.11` se existir e cai para `uv venv -p 3.11` caso contrário.

Sem `make`, os mesmos passos à mão:

```bash
docker compose up -d --wait                # api, db e mock (espera a api ficar "healthy")
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -v
```

Não é preciso criar `.env`: todo valor tem um padrão no compose. A API responde em `http://localhost:3000`, e toda rota (menos `/` e `/health_check`) exige o header `INTERNAL-TOKEN: default_token`.

Mudou `database/database.sql`? Rode `make reset`. Mudou `requirements.txt`? Rode `make rebuild`. Há mais detalhes em [rodando localmente](docs/06-operacao/rodando-localmente.md).

## Repositório AI-friendly

O time trabalha com agentes de código, então as regras do projeto estão escritas para eles também:

- [`AGENTS.md`](AGENTS.md): comandos, regras avaliadas, camadas e limites, lido por Claude Code, Codex, Cursor, Copilot e Gemini CLI.
- [`.agents/skills/`](.agents/README.md): passo a passo para nova rota, novo erro, nova decisão e revisão.
- [`llms.txt`](llms.txt): mapa da documentação.

Detalhes em [trabalhando com IA](docs/trabalhando-com-ia.md).

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
| como usar agentes de IA aqui | [AGENTS.md](AGENTS.md), [docs/trabalhando-com-ia.md](docs/trabalhando-com-ia.md) |
| a RFC da entrega | [docs/rfc/RFC.md](docs/rfc/RFC.md) |

## Estrutura

```
src/        api em camadas: middlewares → schemas → resources → controllers → repositories → models (+ dtos, errors, connectors, utils)
tests/      testes black box por HTTP (integration/) e helpers (utils/)
database/   imagem do Postgres e schema (database.sql)
docs/       documentação navegável; a RFC é derivada dela
.agents/    skills para agentes de IA (o ponto de entrada é o AGENTS.md)
```

## Licença

[MIT](LICENSE)
