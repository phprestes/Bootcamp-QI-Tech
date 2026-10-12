---
title: Camadas do serviço
summary: Caminho da requisição e o que cada pasta de src/ pode e não pode fazer (herdado do bootcamp-base-api).
related: [visao-geral.md, ../03-api/convencoes.md, ../07-testes/estrategia.md]
sources: [bootcamp-base-api/docs/como-o-projeto-e-organizado.md, Aula 1 tarde, Aula 2 p.6-9]
---

> [Índice](../README.md) › Arquitetura › Camadas
>
> **Responde a:** em qual pasta mora cada coisa? quem pode chamar quem? onde fica o commit?

# Camadas do serviço

## Caminho de uma requisição

```
requisição
  → middlewares/    request_context → request_logger → internal_token (403) → session_manager
  → resources/      schema valida o corpo (400) e chama um controller
  → controllers/    regra de negócio e commit
  → repositories/   consultas
  → models/         tabelas
  → dtos/           objeto do banco → JSON
resposta
```

A dependência anda num sentido só: `resources → controllers → repositories → models`. Repository não chama controller; model não conhece rota. Assim cada erro tem um lugar óbvio para procurar e uma camada pode mudar sem arrastar as outras.

## O que cada pasta pode e não pode

| Pasta | Pode | Não pode |
|---|---|---|
| `resources/` | receber a requisição, validar o schema, chamar um controller, escolher o status de sucesso | SQL, regra de negócio, `raise` |
| `schemas/` | descrever o JSON aceito (`additionalProperties: false`) | consultar banco, decidir regra |
| `controllers/` | decidir, chamar repositories e connectors, dar `commit` | escrever consulta, conhecer HTTP |
| `repositories/` | buscar, criar, atualizar | decidir se era permitido |
| `models/` | descrever tabelas | ter regra |
| `dtos/` | montar a resposta | buscar no banco, serializar `id` ou FK |
| `errors/` | código, mensagem e status de cada erro | ter regra |
| `middlewares/` | agir em toda requisição | conhecer uma rota |
| `connectors/` | chamar serviço externo com timeout e traduzir falha | decidir regra, tocar o nosso banco |
| `utils/` | logger, request id, validação de schema, CPF | virar depósito |

Exemplo: `if origin.balance < amount + TRANSFER_FEE_CENTS: raise InsufficientBalance()` mora no `transaction_controller.py`. O único `if` do `transaction_repository.py` decide se a busca leva um filtro, o que é jeito de buscar, não regra.

## Ordem dos middlewares

Em `src/app.py` o último registrado executa primeiro, por isso as linhas aparecem invertidas em relação ao diagrama acima.

- **request_context antes do log:** sem isso as linhas saem com `[-]` no lugar do request id.
- **Log antes do token:** os 403 também aparecem no log, e são eles que mostram alguém tentando adivinhar o token.
- **Sessão por último:** quem foi barrado não chega a pegar sessão.

Nenhum teste cobre essa ordem: trocar as linhas mantém a suíte verde e só aparece no log.

## Sessão de banco

- **Ciclo de vida:** `src/middlewares/session_manager.py` abre o contexto, faz rollback em exceção e fecha sempre. Nunca dá commit.
- **Quem pede:** o `BaseController`, via `get_context()` de `src/database.py`. O resource não sabe que existe banco.
- **Commit:** última linha do controller antes do `return`. Só o controller sabe se o trabalho terminou; com o commit no middleware, um erro depois da gravação não desfaria nada.

A sessão viaja por `contextvars`, o mesmo mecanismo do `request_id`. Por isso qualquer camada *poderia* chamar `get_context()`; o combinado é que só o controller chama.

A sessão é preguiçosa: nasce quando um controller é construído. `/` e `/health_check` não constroem controller e não dependem do banco estar de pé. O preço é que a sessão pode não existir, e todo `rollback`/`close` precisa testar `is not None`. Esquecer isso quebra justamente as rotas sem banco.

O contexto guarda um objeto mutável, não a sessão direto: o `ContextVar` é copiado para a task da rota, então um `.set()` feito lá não chegaria ao middleware, mas a mutação do objeto chega.

## Onde mexer

| Quero… | Mexo em | Depois |
|---|---|---|
| campo novo na entrada | `src/schemas/<verbo>_<recurso>.json` | se for persistido: `database.sql` e `models/` |
| campo novo na resposta | `src/dtos/` | só ali |
| rota nova | `src/resources/` | registrar em `src/app.py`; controller se a regra for nova |
| regra nova | `src/controllers/` | erro em `src/errors/custom_errors.py` se recusar |
| consulta nova | `src/repositories/` | o controller chama |
| tabela nova | `database/database.sql` | `src/models/` e o `__init__.py` |
| algo em toda requisição | `src/middlewares/` | registrar em `src/app.py` |
| chamar outro serviço | `src/connectors/` | chamado pelo controller |

## Armadilhas

| Sintoma | Causa | Correção |
|---|---|---|
| `ModuleNotFoundError` num arquivo novo | falta a linha no `__init__.py` da pasta | acrescentar |
| `ImportError: cannot import name 'Account' from partially initialized module` | ordem do `src/models/__init__.py`: entidade precisa vir depois daquelas de que depende | `Customer`, `AccountStatus`, `Account`, depois o resto |
| `relation "…" does not exist` | `database.sql` só roda quando o banco nasce | `make reset` (apaga os dados) |
| teste quebra depois de mudar `requirements.txt` | a dependência mora na imagem | `make rebuild` |
| passa aqui e quebra no clone | dependência de teste instalada só no seu `.venv` | conferir `requirements-dev.txt`; `make install` recria o `.venv` |

## Schemas e DTOs

`schemas/` cuida do que entra; `dtos/` do que sai.

- O decorator `@SchemaHandler.validate("post_customer.json")` valida o corpo com `jsonschema` antes da rota rodar. JSON Schema em vez de Pydantic: [ADR 0009](decisoes/0009-contrato-em-json-schema.md).
- O DTO transforma o model na resposta: status vira texto, `customer_id` vira `customer_key` (R5). Nada confere o DTO depois; campo interno que entrar ali sai para o cliente.
