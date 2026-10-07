---
title: Fluxo — extrato paginado
summary: GET /account/{account_key}/transactions; paginação limit/page, ordenação, sinal por tipo e reconstrução do saldo.
related: [../03-api/convencoes.md, ../02-arquitetura/decisoes/0003-transacao-tabela-unica-com-tipo.md]
sources: [Aula 1 tarde (extrato paginado), Aula 3 tarde p.18, bootcamp-base-api (paginação)]
---

# Fluxo — extrato

> [Índice](../README.md) › Fluxos › Extrato
>
> **Responde a:** como paginar? em que ordem vêm os lançamentos? o extrato bate com o saldo?

## Caminho feliz

1. O schema de query confere `limit` (1–100, padrão 10), `page` (≥ 0, padrão 0) e `type` (opcional, um dos quatro tipos).
2. O controller busca a conta pela key. Se ela não existe, `404 QIT002007`.
3. O repository faz:

   ```sql
   SELECT … FROM transaction WHERE account_id = :id [AND type_id = :t]
   ORDER BY created_at DESC, id DESC
   LIMIT :limit + 1 OFFSET :page * :limit
   ```

4. O resource monta o envelope:

   ```json
   {
     "data": [
       {"transaction_key": "…", "type": "FEE", "amount": 200, "direction": "DEBIT",
        "counterpart_account_key": "…", "created_at": "2026-10-07T14:00:00Z"}
     ],
     "limit": 10, "page": 0, "is_last_page": true
   }
   ```

   `direction` (`CREDIT`/`DEBIT`) é derivado do tipo no DTO e **não é coluna**.

## Caminhos de falha

| Condição | Resposta |
|---|---|
| `limit=0`, `limit=101`, `page=-1` ou parâmetro desconhecido | `400 QIT000001` |
| Conta inexistente | `404 QIT002007` |
| Página além do fim | `200` com `data: []` e `is_last_page: true` |

## O extrato reconstrói o saldo

`Σ(DEPOSIT + TRANSFER_IN) − Σ(TRANSFER_OUT + FEE) = account.balance`. Um teste percorre todas as páginas e confere a igualdade, provando R4 (nada some) e a atomicidade da transferência.

**Custo conhecido:** a paginação por `OFFSET` fica lenta com anos de extrato. A alternativa é paginar por cursor (`created_at`, `id`), descartada agora porque a query string `limit`/`page` é o contrato pedido em aula.
