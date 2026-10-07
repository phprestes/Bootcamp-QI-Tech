---
title: Registro de decisões (ADRs)
summary: Índice das decisões de arquitetura, cada uma com as alternativas descartadas e o preço de cada uma (R7).
related: [../visao-geral.md, ../../rfc/RFC.md]
sources: [Modelo de RFC (Aula 2), Aula 2 p.66-73]
---

# Decisões de arquitetura

> [Índice](../../README.md) › Arquitetura › Decisões
>
> **Responde a:** por que o sistema é assim? o que foi descartado e quanto custava?

Cada ADR segue o mesmo formato: **Contexto → Decisão → Alternativas descartadas (com preço, e em que cenário ganhariam) → Consequências**. Está escrito no presente, como proposta. A RFC resume estes registros na seção "Explicando a solução de forma macro".

| ADR | Decisão | Status |
|---|---|---|
| [0001](0001-monolito-com-mock-externo.md) | Uma API única com Mockserver no papel do birô | Aceita |
| [0002](0002-saldo-em-coluna-com-lock.md) | O saldo fica em coluna, protegido por `SELECT … FOR UPDATE` e `CHECK >= 0` | Aceita |
| [0003](0003-transacao-tabela-unica-com-tipo.md) | Uma tabela `transaction`, com tipo e tarifa como lançamento próprio | Aceita |
| [0004](0004-dinheiro-em-centavos.md) | Dinheiro em `BIGINT` de centavos | Aceita |
| [0005](0005-uuid-key-publica.md) | `id` interno e `<entidade>_key` UUID na API | Aceita |
| [0006](0006-idempotencia-por-chave.md) | `request_control_key` no corpo + `UNIQUE` | Aceita |
| [0007](0007-convencao-de-rotas.md) | Item no singular, lista no plural, sem versão na URL | Aceita |

Para incluir uma decisão nova, copie um ADR, use o próximo número e adicione a linha nesta tabela e no [`llms.txt`](../../../llms.txt).
