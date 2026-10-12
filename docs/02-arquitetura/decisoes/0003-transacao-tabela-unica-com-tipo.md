---
title: "ADR 0003: Uma tabela transaction, com tipo; tarifa é lançamento próprio"
summary: Depósito, transferência e tarifa são linhas da mesma tabela, uma por conta afetada, com type que define o sinal.
related: [../../04-dados/modelo.md, ../../05-fluxos/transferencia.md, ../../05-fluxos/extrato.md]
sources: [Aula 2 p.24 (Desenho A × B), Aula 2 p.32 (R$200 + R$2 de tarifa)]
---

# ADR 0003: Uma tabela `transaction`, com tipo; a tarifa é um lançamento próprio

> [Índice](../../README.md) › [Decisões](README.md) › 0003

**Status:** aceita

## Contexto

A aula comparou dois desenhos:

- **(A)** Uma tabela com coluna `type` e uma rota `POST /account/{key}/transaction`.
- **(B)** Uma tabela por tipo, com rotas `/deposit` e `/transfer`.

O extrato precisa listar tudo o que mexeu numa conta, em ordem, e reconstruir o saldo.

## Decisão

- Tabela `transaction` com uma linha por conta afetada e `amount BIGINT > 0`. O sinal vem do `transaction_type`:

  | type | Efeito na conta da linha | Quando nasce |
  |---|---|---|
  | `DEPOSIT` | crédito | depósito |
  | `TRANSFER_OUT` | débito | transferência, na origem |
  | `TRANSFER_IN` | crédito | transferência, no destino |
  | `FEE` | débito | tarifa da transferência, na origem |

- Uma transferência grava três linhas no mesmo commit: `TRANSFER_OUT`, `TRANSFER_IN` e `FEE`.
  - As linhas `TRANSFER_IN` e `FEE` apontam para a `TRANSFER_OUT` por `origin_transaction_id`.
  - `counterpart_account_id` registra a outra ponta.
- A tarifa é configurável via `TRANSFER_FEE_CENTS` (padrão 200, que é R$ 2,00). O valor efetivamente cobrado fica gravado na própria linha `FEE`, e é por isso que mudar a configuração não reescreve o passado.

## Alternativas descartadas

- **Uma tabela por tipo (deposit, transfer, fee).**
  - **Preço:** o extrato vira um `UNION` de três consultas, e toda regra comum (paginação, ordenação, idempotência) é escrita três vezes.
  - **Ganharia se** os tipos tivessem campos muito diferentes, como dados de boleto ou de Pix.
- **Uma linha por transferência, com origem e destino.**
  - **Preço:** o extrato de uma conta precisa olhar duas colunas e decidir o sinal em código. A tarifa ou vira coluna (e some do extrato) ou vira outra tabela.
  - **Ganharia se** o relatório principal fosse "transferências do sistema", e não "extrato da conta".
- **Tarifa como coluna `fee` na linha da transferência.**
  - **Preço:** o extrato não mostra a tarifa como lançamento e a soma das linhas não reconstrói o saldo sem regra especial.

## Consequências

- Extrato = `SELECT … FROM transaction WHERE account_id = :id ORDER BY created_at DESC, id DESC`. Uma consulta só.
- `balance = SUM(DEPOSIT + TRANSFER_IN) - SUM(TRANSFER_OUT + FEE)` vira um invariante testável.
- O tipo é uma tabela enumeradora (`transaction_type`), e o DTO converte o id em texto.
