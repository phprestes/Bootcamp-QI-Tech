---
title: Rodando localmente
summary: Comandos para subir, testar, resetar o banco e reconstruir a imagem; armadilhas comuns e o ensaio da banca.
related: [../07-testes/estrategia.md, ../referencia/base-service-readme.md, observabilidade.md]
sources: [Aula 3 manhã p.29-33, Guia Dia 3, bootcamp-base-api README]
---

# Rodando localmente

> [Índice](../README.md) › Operação › Rodando localmente
>
> **Responde a:** como subo tudo? como rodo os testes? o que fazer quando mudo o SQL ou as dependências?

Pré-requisitos:

- Docker com Compose v2.
- `make` (opcional, atalho para os comandos abaixo).
- Python 3.11, só para rodar o `pytest` na máquina. Não use 3.12+: o SQLAlchemy 2.0.23 fixado no projeto quebra no import (`uv venv -p 3.11` resolve se o sistema tiver outra versão).

Não é preciso criar `.env`: todo valor tem um padrão `${VAR:-padrão}` no compose.

## Do clone ao verde (o que a banca faz)

```bash
git clone <repo> && cd <repo>
make all                             # up --wait + .venv 3.11 + pytest -v
```

Sem `make`:

```bash
docker compose up -d --wait          # api, db, mock e pgadmin; espera api ficar (healthy)
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -v
```

O `make install` só recria o `.venv` quando `requirements*.txt` muda. Usa `python3.11` se existir; senão, `uv venv -p 3.11`.

> **Antes de entregar:** apague a pasta, clone de novo e rode exatamente os comandos acima, em Linux. "Se para subir é preciso mais de um comando, falta alguma coisa no compose."

## Dia a dia

| Quero… | `make` | Comando equivalente | Por quê |
|---|---|---|---|
| ver todos os alvos | `make` | — | lista com descrição |
| subir tudo | `make up` | `docker compose up -d --build --wait` | volta só quando tudo está `healthy` |
| rodar os testes | `make test` | `pytest -v` | precisa do `make up` antes |
| cobertura | `make test-cov` | `pytest --cov` | |
| ver o estado | `make ps` | `docker compose ps` | mostra `healthy` e `unhealthy` |
| ver o log da API | `make logs` | `docker compose logs -f api` | é o primeiro lugar onde olhar |
| parar e manter os dados | `make stop` | `docker compose stop` | o volume fica |
| **mudei `database/database.sql`** | `make reset` | `docker compose down -v && docker compose up -d --build --wait` | o SQL só roda quando o banco nasce |
| **mudei `requirements.txt`** | `make rebuild` | `docker compose build --no-cache api && docker compose up -d --wait` | a dependência mora na imagem |
| entrar no container | `make shell` | `docker compose exec api sh` | inspecionar sem instalar nada |
| lint | `make lint` | `flake8 src tests` | precisa sair sem nenhum apontamento |
| lint e testes | `make check` | | antes de abrir PR |
| limpar tudo | `make clean` | `docker compose down -v && rm -rf .venv` | apaga dados do banco |

O código em `src/` é montado no container e roda com `--reload`: salvou, recarregou.

## Olhar o banco (pgAdmin)

O `make up` também sobe o pgAdmin em `http://localhost:5050`. Entre com `admin@bootcamp.com` / `bootcamp` e registre o servidor: host `db`, porta `5432`, banco, usuário e senha `bootcamp`. Serve só para inspecionar; prepare cenário de teste pela API (R1).

## Variáveis de ambiente

| Variável | Padrão | Uso |
|---|---|---|
| `INTERNAL_TOKEN` | `default_token` | Token exigido nas rotas; os testes leem o mesmo valor |
| `API_PORT` / `DB_PORT` / `MOCK_PORT` / `PGADMIN_PORT` | 3000 / 5432 / 1080 / 5050 | Trocar se a porta estiver ocupada |
| `PGADMIN_DEFAULT_EMAIL` / `PGADMIN_DEFAULT_PASSWORD` | `admin@bootcamp.com` / `bootcamp` | Login do pgAdmin |
| `BUREAU_API_URL` | `http://mock:1080/bureau` (no compose) | Endereço do birô |
| `BUREAU_API_TIMEOUT` | 5 | Segundos de espera pelo birô |
| `TRANSFER_FEE_CENTS` | 200 | Tarifa por transferência, em centavos |
| `MAX_ACCOUNTS_PER_CUSTOMER` | 3 | Limite de contas não encerradas por cliente |
| `APP_ENV` | `local` | `local`/`test` usam log DEBUG; `production` usa INFO |

## Armadilhas

| Sintoma | Causa | Correção |
|---|---|---|
| `relation "…" does not exist` | O SQL mudou, mas o volume é antigo | `make reset` |
| `ModuleNotFoundError` dentro da API | A dependência nova não está na imagem | `make rebuild` |
| `port is already allocated` | A porta já está em uso | `API_PORT=3001` no `.env` |
| `403` em todo teste | Token diferente entre o compose e o `.env` dos testes | Use o mesmo `INTERNAL_TOKEN` |
| Primeiro teste falha com conexão recusada | A API ainda não está `healthy` | Use `make up` (espera o healthcheck) |
| `ImportError` do SQLAlchemy no pytest | `.venv` criado com Python 3.12+ | `rm -rf .venv && make install` |

Para o troubleshooting completo do serviço-base, veja o [README original](../referencia/base-service-readme.md#3-quando-dá-errado).
