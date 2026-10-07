---
title: Resiliência
summary: Timeout no connector do birô, tradução de falha externa em 502, quando repetir, idempotência e escala horizontal.
related: [../05-fluxos/criar-cliente.md, ../02-arquitetura/decisoes/0006-idempotencia-por-chave.md, observabilidade.md]
sources: [Dia 4 manhã notas 23-35, One-page Dia 4, Autoestudo Aula 4 #4-6, Aula 2 p.8-9 (connectors)]
---

# Resiliência

> [Índice](../README.md) › Operação › Resiliência
>
> **Responde a:** quanto tempo a API espera o birô? o que devolve se ele cair? é seguro repetir?

## Timeout no connector

- O `requests` **não tem timeout padrão**: sem o parâmetro, a chamada pode esperar para sempre. Uma dependência lenta prende a conexão de banco e represa as requisições, até a API parar de responder sem estar caída.
- O `BureauConnector` herda de `RestConnector` e usa `BUREAU_API_TIMEOUT` (padrão 5s), escolhido para este serviço.
- **O connector traduz e o controller decide.** O `BureauConnector` converte "não respondeu" (timeout, conexão caída) em `BureauUnavailable`. O `CustomerController._check_bureau` decide o que cada resposta significa: 5xx ou corpo sem `situation` também viram `BureauUnavailable`. Em todos os casos sai `502 QIT002006` e nada é gravado.
- **Nenhuma chamada externa acontece com lock aberto.** O birô é consultado antes de qualquer `FOR UPDATE`.

| Resposta do birô | Interpretação (controller) | HTTP |
|---|---|---|
| `200 {"situation": "REGULAR"}` | segue | — |
| `200 {"situation": "SUSPENDED" \| "CANCELED" \| …}` | CPF irregular | `422 QIT002005` |
| `404` | CPF desconhecido, tratado como irregular | `422 QIT002005` |
| timeout, erro de conexão, 5xx, corpo sem `situation` | birô indisponível | `502 QIT002006` |

Como testar: o Mockserver é configurado com `delay` maior que o timeout, e o teste espera 502. Ver [estratégia de testes](../07-testes/estrategia.md).

## Retry

- **A API não faz retry automático no birô.** Ela devolve 502 rápido, e quem chamou decide.
- Retry só é seguro quando a operação é idempotente:
  - `POST /customer` falha antes de gravar e tem `UNIQUE(document_number)`.
  - `POST /…/transaction` usa `request_control_key` ([ADR 0006](../02-arquitetura/decisoes/0006-idempotencia-por-chave.md)).
- Recomendação a quem chama: backoff exponencial com jitter, mantendo a **mesma** `request_control_key`.
- Circuit breaker: fora do escopo. Seria o próximo passo se o birô caísse com frequência.

## Escala

- A API é stateless, com a sessão por requisição, então N réplicas atrás de um load balancer funcionam sem mudança de código.
- O lock pessimista funciona entre réplicas porque quem trava é o Postgres, não a memória da réplica.
- **Escalar a API não escala o banco.** Cada réplica abre o próprio pool, e o limite real é `max_connections` do Postgres.

## A regra para levar (Dia 4)

> Antes de dizer que está pronto: **quem pode pedir isso** ([segurança](seguranca.md)), **quanto tempo eu espero** (timeout), **o que acontece se pedirem duas vezes** (idempotência) e **como eu vou saber que falhou** ([observabilidade](observabilidade.md))?
