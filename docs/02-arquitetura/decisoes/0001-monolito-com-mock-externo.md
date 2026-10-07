---
title: "ADR 0001 — Monólito com Mockserver no papel do birô"
summary: Uma API única para cliente, conta e transação; o birô de CPF é externo e simulado pelo Mockserver.
related: [../visao-geral.md, ../../06-operacao/resiliencia.md, ../../07-testes/estrategia.md]
sources: [Aula 3 tarde p.21-25, Aula 3 manhã p.33, Dia 4 manhã nota 22]
---

# ADR 0001 — Monólito com Mockserver no papel do birô

> [Índice](../../README.md) › [Decisões](README.md) › 0001

**Status:** aceita

## Contexto

A aula mostrou um ecossistema com três serviços: clientes chamam a Receita, contas chamam clientes e transações chamam contas. O prazo é curto, o time tem até três pessoas e a banca roda tudo numa máquina limpa (R2). A transferência precisa de atomicidade entre o débito, o crédito e a tarifa.

## Decisão

Uma API (`api`) com os três recursos e um banco (`db`). O único serviço externo é o **birô de CPF**, consultado por um connector com timeout. No compose e nos testes, quem responde por ele é o `mock` (MockServer).

## Alternativas descartadas

- **Três APIs separadas (customers, accounts, transactions)**, cada uma com o próprio banco.
  - **Preço:** a transferência vira uma transação distribuída (saga ou compensação), com três vezes mais compose, tokens e testes.
  - **Ganharia se** os times e os ritmos de deploy fossem independentes, ou se a escala de leitura do extrato fosse muito diferente da de escrita.
- **Worker assíncrono para a transferência.**
  - **Preço:** a resposta deixa de ser final, porque o cliente precisa consultar o status depois, e entra uma fila na infraestrutura.
  - **Ganharia se** a liquidação dependesse de um sistema externo lento, como Pix ou TED.
- **Não consultar birô nenhum.**
  - **Preço:** perde a parte de connector, timeout e 502, que as aulas cobram.
  - **Ganharia se** o cadastro fosse só interno, sem KYC.

## Consequências

- Um `commit` por requisição garante ACID na transferência sem coordenação entre serviços.
- O ecossistema da RFC mostra `api`, `db` e `mock`, e explica o que muda em produção (gateway, réplicas e birô real).
- Se a fase final pedir um segundo serviço, ele entra como mais um serviço no compose e aparece na RFC.
