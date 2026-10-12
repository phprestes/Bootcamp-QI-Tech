---
title: "ADR 0007: Convenção de rotas"
summary: Substantivo em inglês, item no singular e lista no plural (padrão do base-service), sem versão nem prefixo; ação de estado vira sub-recurso.
related: [../../03-api/convencoes.md, ../../03-api/rotas.md]
sources: [Aula 2 p.21-22 ("escolham uma e escrevam na RFC"), bootcamp-base-api, biblioteca-api]
---

# ADR 0007: Convenção de rotas

> [Índice](../../README.md) › [Decisões](README.md) › 0007

**Status:** aceita

## Contexto

A aula pediu que cada time escolhesse uma convenção de singular e plural e a registrasse. Os slides mostram `/accounts` em uns lugares e `/account` em outros. O base-service e a biblioteca usam item no singular e lista no plural.

## Decisão

- **Item no singular:** `POST /customer`, `GET /customer/{customer_key}`.
- **Lista no plural:** `GET /customers`, `GET /account/{account_key}/transactions`.
- **Aninhamento só onde há posse:**
  - `POST /customer/{customer_key}/account`, porque a conta pertence ao cliente.
  - `POST /account/{account_key}/transaction`, porque a transação pertence à conta.
- **Mudança de estado vira sub-recurso via `PUT`:** `PUT /account/{account_key}/status`.
- Sem `/v1` e sem prefixo de serviço, como no base-service.
- Path e campos em `snake_case` e em inglês.

## Alternativas descartadas

- **Tudo no plural (`/customers/{key}`).**
  - **Preço:** quebra o padrão do código-base que o time vai copiar, e as duas formas acabariam misturadas.
  - **Ganharia se** o projeto começasse do zero ou seguisse um guia externo, como Google AIP ou Microsoft.
- **Rotas por ação (`/deposit`, `/transfer`).**
  - **Preço:** o verbo vai para a URL, o que viola o REST da aula. Ver [ADR 0003](0003-transacao-tabela-unica-com-tipo.md).
  - **Ganharia se** depósito e transferência fossem tabelas separadas, com corpos muito diferentes.
- **Versionar com `/v1`.**
  - **Preço:** nenhum cliente externo justifica isso agora.
  - **Ganharia se** a API fosse pública, com integrações de terceiros.

## Consequências

Toda rota nova segue esta tabela, e o code review recusa as que fogem dela.
