# AGENTS.md

Instruções para agentes de código, no formato [agents.md](https://agents.md). Pessoas começam pelo [README](README.md); o porquê deste arquivo está em [docs/trabalhando-com-ia.md](docs/trabalhando-com-ia.md).

## Projeto

API de banco digital do Bootcamp QI Tech 2026: cliente, conta, depósito, transferência com tarifa e extrato paginado. Python 3.11, FastAPI, SQLAlchemy 2, PostgreSQL 16, jsonschema e Docker Compose (`api`, `db`, `mock` = MockServer no papel do birô de CPF, `pgadmin` só para inspecionar o banco). Nasceu do `bootcamp-base-api`: o exemplo `sample_entity` foi trocado por `customer`, `account` e `transaction`, cobertos por 78 testes black box.

Entrega da fase 1: 12/10, até 12h, repositório público no GitHub + PDF da RFC. A banca avalia o repositório como estiver nesse momento.

A documentação é a fonte da verdade. Comece por [docs/README.md](docs/README.md) ou pelo [llms.txt](llms.txt). As decisões ficam em [docs/02-arquitetura/decisoes/](docs/02-arquitetura/decisoes/README.md). A [RFC](docs/rfc/RFC.md) é derivada dos documentos: mude o documento primeiro.

## Comandos

```bash
make                # lista os alvos
make all            # sobe api/db/mock/pgadmin (espera healthy), cria .venv 3.11 e roda pytest -v
make up             # só sobe
make test           # só testa (precisa do make up)
make lint           # flake8 src tests; precisa sair limpo
make reset          # depois de mudar database/database.sql
make rebuild        # depois de mudar requirements.txt
make logs           # log da api
```

Use Python 3.11: o SQLAlchemy 2.0.23 quebra no 3.12+. O `make install` já resolve isso.

## Regras que não se negociam (avaliadas)

- **R1.** Teste nunca importa de `src/` e nunca lê o banco. Prepare o cenário pela API (POST), não por INSERT.
- **R2.** Um comando sobe tudo numa máquina Linux limpa. Nenhum passo manual.
- **R3.** Toda recusa é uma classe em `src/errors/custom_errors.py` com código `QIT` único. O próximo livre está em [docs/03-api/erros.md](docs/03-api/erros.md). Corpo: `{title, description, translation, code}`.
- **R4.** `transaction` e `account_status_event` são append-only.
- **R5.** Só `<entidade>_key` (UUID gerado no repository) sai da API; nunca `id`.
- **R6.** Dinheiro é `BIGINT` em centavos; nunca float.
- **R8.** Recurso de outro dono devolve 404, nunca 403.

## Camadas

| Pasta | Faz | Não faz |
|---|---|---|
| `resources/` | HTTP de entrada e saída; escolhe o status de sucesso | regra de negócio, `raise` |
| `controllers/` | regras de negócio; chama repositories e connectors; único `session.commit()`, como última linha antes do `return` | SQL direto |
| `repositories/` | consultas; `with_for_update()` em ler-decidir-escrever | decidir |
| `connectors/` | HTTP externo com timeout obrigatório; traduz falha em erro nosso | decidir |
| `schemas/` | JSON Schema com `additionalProperties: false`; só formato | validar verdade |
| `dtos/` | forma da saída | serializar `id` ou FK |

- Trave contas em ordem crescente de `id`. Nunca chame HTTP externo segurando trava.
- Idempotência: `request_control_key` no corpo + `UNIQUE`. Mesmo corpo devolve 200 com o original; corpo diferente devolve 409.

Detalhe em [docs/02-arquitetura/camadas.md](docs/02-arquitetura/camadas.md).

## Como trabalhar

- **TDD.** Nenhuma linha nova em `src/` sem um teste vermelho pedindo. Todo `if` ganha um teste que passa e um que é recusado.
- **Nome de teste:** `test_<ação>_<cenário>_returns_<status>`, com docstring citando a regra (RNxx/Rx).
- **Idioma:** código, rotas e campos em inglês; prosa da documentação e `translation` dos erros em português.
- **Comentários** explicam o porquê, em uma ou duas linhas. Raciocínio longo vai para `docs/` e o código aponta para lá.
- **Documentação junto com o código:** rota nova atualiza [rotas.md](docs/03-api/rotas.md); erro novo atualiza [erros.md](docs/03-api/erros.md); decisão nova vira ADR e entra no `llms.txt`.
- **Commits:** Conventional Commits (`feat(transaction): …`), sem trailers de co-autoria ou de ferramenta. Não faça commit sem pedido.
- **Antes de dizer que terminou:** `make reset check` precisa passar.

## Skills

Receitas passo a passo para tarefas recorrentes ficam em [`.agents/skills/`](.agents/README.md), uma pasta por tarefa com um `SKILL.md`. Leia a skill da tarefa antes de começar.

## Limites

- Não leia, crie nem versione `.env` com segredo real.
- Não altere `docker-compose.yml`, `Dockerfile` ou `database/database.sql` sem pedido explícito: mexem em R2.
- Não apague nem reescreva teste existente para fazê-lo passar.
