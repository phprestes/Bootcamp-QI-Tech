---
title: Rotas
summary: Tabela de todas as rotas com método, caminho, entrada relevante, saídas com status/código e idempotência.
related: [convencoes.md, erros.md, ../05-fluxos/transferencia.md]
sources: [Modelo de RFC (seção Rotas), RFC da biblioteca (Aula 3), Aula 3 tarde p.18]
---

# Rotas

> [Índice](../README.md) › API › Rotas
>
> **Responde a:** quais rotas existem? o que cada uma recebe, devolve e recusa? qual é idempotente?

Valores monetários são **inteiros em centavos**. Todas as rotas, exceto `/` e `/health_check`, exigem `INTERNAL-TOKEN`; sem ele, a resposta é `403 QIT000002`. Qualquer corpo ou query fora do schema devolve `400 QIT000001`.

## Serviço

| Método | Caminho | O que faz | Entrada | Saídas |
|---|---|---|---|---|
| `GET` | `/` | Identifica o serviço | — | `200` |
| `GET` | `/health_check` | Diz se a API está de pé, sem tocar o banco | — | `204` |

## Cliente

| Método | Caminho | O que faz | Entrada (campos que importam) | Saídas (status e quando) | Idempotente? |
|---|---|---|---|---|---|
| `POST` | `/customer` | Cadastra um cliente depois de consultar o birô | `name`, `document_number` (`000.000.000-00`), `birthdate` (`YYYY-MM-DD`) | `201 {customer_key}`; `422 QIT002003` dígito verificador inválido; `422 QIT002004` menor de 18; `422 QIT002017` data de nascimento inexistente ou futura; `422 QIT002005` CPF irregular no birô; `409 QIT002002` CPF já cadastrado; `502 QIT002006` birô indisponível | Sim, por `UNIQUE(document_number)`: repetir devolve 409 e não cria outro |
| `GET` | `/customer/{customer_key}` | Devolve o cliente | key no path | `200`; `404 QIT002001` | — |
| `GET` | `/customers` | Lista clientes, paginado | `limit`, `page`, `document_number` (opcional) | `200` com o envelope de página | — |
| `GET` | `/customer/{customer_key}/accounts` | Lista as contas do cliente | `limit`, `page` | `200`; `404 QIT002001` | — |

## Conta

| Método | Caminho | O que faz | Entrada | Saídas | Idempotente? |
|---|---|---|---|---|---|
| `POST` | `/customer/{customer_key}/account` | Abre uma conta `ACTIVE`, com saldo 0 | key no path | `201 {account_key, status, balance}`; `404 QIT002001` cliente inexistente; `409 QIT002008` limite de contas atingido | Não. Cada POST abre uma conta nova, até o limite |
| `GET` | `/account/{account_key}` | Devolve conta, saldo, `customer_key` e o histórico de status | key no path | `200`; `404 QIT002007` | — |
| `PUT` | `/account/{account_key}/status` | Muda o estado da conta | `status` ∈ `ACTIVE`, `BLOCKED`, `CLOSED`; `reason` | `200 {account_key, status, balance}`; `404 QIT002007`; `409 QIT002010` transição inválida (inclui sair de `CLOSED` e pedir o estado atual); `409 QIT002011` encerrar com saldo diferente de 0 | Não. Repetir o mesmo estado devolve 409 |

## Transação

| Método | Caminho | O que faz | Entrada | Saídas | Idempotente? |
|---|---|---|---|---|---|
| `POST` | `/account/{account_key}/transaction` | Depósito (`DEPOSIT`) ou transferência (`TRANSFER`) a partir da conta do path | `type`, `amount` (≥ 1), `request_control_key` (UUID), `destination_account_key` (obrigatória se `TRANSFER`) | `201 {transaction_key, type, amount, fee, balance}`; `200` mesmo corpo da primeira resposta (repetição); `404 QIT002007` conta do path; `404 QIT002014` destino; `409 QIT002009` origem ou destino não `ACTIVE`; `409 QIT002016` chave reutilizada com corpo diferente; `422 QIT002012` saldo insuficiente para valor + tarifa; `422 QIT002013` destino igual à origem | **Sim**, por `UNIQUE(request_control_key)`. Ver [ADR 0006](../02-arquitetura/decisoes/0006-idempotencia-por-chave.md) |
| `GET` | `/account/{account_key}/transactions` | Extrato paginado da conta | `limit`, `page`, `type` (opcional) | `200 {data, limit, page, is_last_page}`; `404 QIT002007` | — |
| `GET` | `/account/{account_key}/transaction/{transaction_key}` | Detalhe de um lançamento **da conta** | keys no path | `200`; `404 QIT002007`; `404 QIT002015` lançamento inexistente ou de outra conta (R8) | — |

## Exemplos

```http
POST /account/0b0c…/transaction
INTERNAL-TOKEN: <token>
Content-Type: application/json

{
  "type": "TRANSFER",
  "amount": 20000,
  "destination_account_key": "7f2e…",
  "request_control_key": "c9a1…"
}
```

```http
HTTP/1.1 201 Created
X-Request-ID: 4b1d…

{ "transaction_key": "e3d2…", "type": "TRANSFER_OUT", "amount": 20000, "fee": 200, "balance": 79800 }
```
