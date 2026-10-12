---
title: "ADR 0005: id interno, key UUID pública"
summary: Tabelas têm id serial (FKs, ordenação) e <entidade>_key CHAR(36) UNIQUE, a única que sai na API (R5).
related: [../../03-api/convencoes.md, ../../06-operacao/seguranca.md]
sources: [Aula 2 p.25-27, One-page Dia 2 (Id e key), Autoestudo Aula 2 nº 7]
---

# ADR 0005: `id` interno, `key` UUID pública

> [Índice](../../README.md) › [Decisões](README.md) › 0005

**Status:** aceita

## Contexto

Com `/account/2` na URL, qualquer um percorre a base contando de 1 em diante, e o número ainda revela o volume do negócio (R5).

## Decisão

- Toda tabela de domínio tem `id SERIAL PRIMARY KEY`, usado em FK, join e desempate de ordenação.
- Toda tabela de domínio também tem `<entidade>_key CHAR(36) NOT NULL UNIQUE`, um UUID v4 gerado no repository no `create`.
- Só a `_key` aparece em URL, corpo de requisição e resposta. O DTO nunca serializa `id` nem FK numérica.

## Alternativas descartadas

- **UUID como PK.**
  - **Preço:** índice maior e FKs mais pesadas. A base da aula já usa id + key, e mudar quebraria o padrão.
  - **Ganharia se** os ids fossem gerados em vários serviços sem coordenação.
- **id sequencial exposto + checagem de dono.**
  - **Preço:** resolve a autorização, mas não o vazamento de volume nem a enumeração.
  - **Ganharia se** o volume não fosse segredo e o identificador precisasse ser curto e legível, como um número de protocolo.

## Consequências

- Um teste confere que nenhuma resposta tem campo `id` ou campo terminado em `_id`.
- As buscas por key usam índice `UNIQUE`.
