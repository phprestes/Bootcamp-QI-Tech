---
title: Fluxo — depósito
summary: POST /account/{account_key}/transaction com type DEPOSIT; idempotência, lock da conta, lançamento e saldo.
related: [transferencia.md, ../02-arquitetura/decisoes/0006-idempotencia-por-chave.md]
sources: [Aula 2 p.24, Dia 4 notas 28-29]
---

# Fluxo — depósito

> [Índice](../README.md) › Fluxos › Depósito
>
> **Responde a:** o que acontece num depósito? e se ele for repetido?

## Caminho feliz

1. O schema confere `type = DEPOSIT`, `amount ≥ 1` e `request_control_key` UUID.
2. O repository busca uma transação com essa `request_control_key`. Se não encontra, o fluxo segue.
3. O controller trava a conta (`with_for_update()`). Se ela não existe, `404 QIT002007`; se não está `ACTIVE`, `409 QIT002009`.
4. O controller faz `INSERT transaction (DEPOSIT, amount, request_control_key)`.
5. Atualiza `account.balance += amount` e `updated_at`.
6. Faz commit e responde `201 {transaction_key, type: "DEPOSIT", amount, fee: 0, balance}`.

## Caminhos de falha

| Condição | Resposta |
|---|---|
| A chave já existe com o mesmo corpo | `200` com o DTO original, sem gravar nada |
| A chave já existe com outro corpo | `409 QIT002016` |
| Dois pedidos simultâneos com a mesma chave nova | O segundo bate no `UNIQUE` e é tratado como repetição (`200`) |
| Conta `BLOCKED` ou `CLOSED` | `409 QIT002009` |
