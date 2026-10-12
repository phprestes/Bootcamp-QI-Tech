---
title: Catálogo de erros
summary: Todo código QIT que a API devolve, com status HTTP, quando sai e a classe correspondente em src/errors/.
related: [convencoes.md, rotas.md, ../01-contexto/requisitos.md]
sources: [bootcamp-base-api src/errors, Dia 4 manhã notas 10-11 (erros nomeados)]
---

# Catálogo de erros

> [Índice](../README.md) › API › Erros
>
> **Responde a:** qual código sai em cada recusa? qual classe levanta? qual é o próximo código livre?

O corpo de todo erro é `{title, description, translation, code}`, conforme [convenções](convencoes.md#formato-de-erro-r3). Os códigos são únicos, e o boot falha se houver dois iguais.

## Faixas

| Faixa | Uso | Onde |
|---|---|---|
| `QIT000xxx` | Genéricos da infraestrutura | `src/errors/base_error.py` (herdado do base-service) |
| `QIT001xxx` | Exemplo `sample_entity` do base-service | Removidos com o exemplo; não reutilizar |
| `QIT002xxx` | Domínio do banco | `src/errors/custom_errors.py` |

## Genéricos (herdados)

| Código | HTTP | Classe | Quando |
|---|---|---|---|
| `QIT000001` | 400 | `InvalidSchema` | Corpo ou query fora do schema |
| `QIT000002` | 403 | `ForbiddenNotInternal` | `INTERNAL-TOKEN` ausente ou errado |
| `QIT000010` | 400 | `InvalidParameter` | Parâmetro de path ou query com tipo inválido. Reservado: hoje o schema barra antes |
| `QIT000404` | 404 | `NotFoundResource` | Rota inexistente |
| `QIT000405` | 405 | `MethodNotAllowed` | Método não aceito |
| `QIT000500` | 500 | `InternalError` | Exceção não tratada. É registrada com `logger.exception` |

## Domínio

| Código | HTTP | Classe | Quando | Regra |
|---|---|---|---|---|
| `QIT002001` | 404 | `NotFoundCustomer` | `customer_key` inexistente | RN07 |
| `QIT002002` | 409 | `DuplicatedDocumentNumber` | CPF já cadastrado | RN03 |
| `QIT002003` | 422 | `InvalidDocumentNumber` | Dígitos verificadores do CPF não batem | RN02 |
| `QIT002004` | 422 | `UnderageCustomer` | Menor de 18 anos | RN04 |
| `QIT002005` | 422 | `IrregularDocumentNumber` | O birô diz que o CPF não está `REGULAR` (ou não o conhece) | RN05 |
| `QIT002006` | 502 | `BureauUnavailable` | O birô estourou o timeout, respondeu 5xx ou mandou corpo inesperado | RN06 |
| `QIT002007` | 404 | `NotFoundAccount` | `account_key` do path inexistente | — |
| `QIT002008` | 409 | `AccountLimitReached` | O cliente já tem `MAX_ACCOUNTS_PER_CUSTOMER` contas não encerradas | RN08 |
| `QIT002009` | 409 | `AccountNotActive` | Origem ou destino em `BLOCKED` ou `CLOSED` | RN12 |
| `QIT002010` | 409 | `InvalidStatusTransition` | Transição fora da [máquina de estados](../04-dados/estados.md) | RN10 |
| `QIT002011` | 409 | `AccountHasBalance` | Tentativa de encerrar conta com saldo diferente de 0 | RN11 |
| `QIT002012` | 422 | `InsufficientBalance` | Saldo menor que valor + tarifa | RN14 |
| `QIT002013` | 422 | `SameAccountTransfer` | Destino igual à origem | RN15 |
| `QIT002014` | 404 | `NotFoundDestinationAccount` | `destination_account_key` inexistente | RN16 |
| `QIT002015` | 404 | `NotFoundTransaction` | Lançamento inexistente **ou de outra conta** | RN20 / R8 |
| `QIT002016` | 409 | `RequestControlKeyConflict` | `request_control_key` já usada com outro corpo | RN19 |
| `QIT002017` | 422 | `InvalidBirthdate` | Data de nascimento inexistente (`1990-02-30`) ou no futuro | RN04a |

**Próximo código livre: `QIT002018`.** Atualize esta linha a cada erro novo.
