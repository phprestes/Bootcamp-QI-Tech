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
- Python 3.11, só para rodar o `pytest` na máquina. **Não use 3.12+**: o SQLAlchemy 2.0.23 fixado no projeto quebra no import (`uv venv -p 3.11` resolve se o sistema tiver outra versão).

Não é preciso criar `.env`: todo valor tem um padrão `${VAR:-padrão}` no compose.

## Do clone ao verde (o que a banca faz)

```bash
git clone <repo> && cd <repo>
docker compose up -d                 # api, db e mock; espere api ficar (healthy)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -v
```

> **Antes de entregar:** apague a pasta, clone de novo e rode exatamente os comandos acima, em Linux. "Se para subir é preciso mais de um comando, falta alguma coisa no compose."

## Dia a dia

| Quero… | Comando | Por quê |
|---|---|---|
| ver o estado | `docker compose ps` | mostra `healthy` e `unhealthy` |
| ver o log da API | `docker compose logs -f api` | é o primeiro lugar onde olhar |
| parar e manter os dados | `docker compose stop` | o volume fica |
| **mudei `database/database.sql`** | `docker compose down -v && docker compose up -d --build` | o SQL só roda quando o banco nasce |
| **mudei `requirements.txt`** | `docker compose build --no-cache api && docker compose up -d` | a dependência mora na imagem |
| entrar no container | `docker compose exec api sh` | inspecionar sem instalar nada |
| lint | `python3 -m flake8 .` | precisa sair sem nenhum apontamento |

O código em `src/` é montado no container e roda com `--reload`: salvou, recarregou.

## Variáveis de ambiente

| Variável | Padrão | Uso |
|---|---|---|
| `INTERNAL_TOKEN` | `default_token` | Token exigido nas rotas; os testes leem o mesmo valor |
| `API_PORT` / `DB_PORT` / `MOCK_PORT` | 3000 / 5432 / 1080 | Trocar se a porta estiver ocupada |
| `BUREAU_API_URL` | `http://mock:1080/bureau` (no compose) | Endereço do birô |
| `BUREAU_API_TIMEOUT` | 5 | Segundos de espera pelo birô |
| `TRANSFER_FEE_CENTS` | 200 | Tarifa por transferência, em centavos |
| `MAX_ACCOUNTS_PER_CUSTOMER` | 3 | Limite de contas não encerradas por cliente |
| `APP_ENV` | `local` | `local`/`test` usam log DEBUG; `production` usa INFO |

## Armadilhas

| Sintoma | Causa | Correção |
|---|---|---|
| `relation "…" does not exist` | O SQL mudou, mas o volume é antigo | `docker compose down -v` |
| `ModuleNotFoundError` dentro da API | A dependência nova não está na imagem | `build --no-cache api` |
| `port is already allocated` | A porta já está em uso | `API_PORT=3001` no `.env` |
| `403` em todo teste | Token diferente entre o compose e o `.env` dos testes | Use o mesmo `INTERNAL_TOKEN` |
| Primeiro teste falha com conexão recusada | A API ainda não está `healthy` | Espere o `docker compose ps` |

Para o troubleshooting completo do serviço-base, veja o [README original](../referencia/base-service-readme.md#3-quando-dá-errado).
