---
title: "ADR 0006 — Idempotência por request_control_key"
summary: Quem chama gera um UUID por operação e o envia no corpo; o banco garante unicidade; repetir devolve a resposta original.
related: [../../05-fluxos/transferencia.md, ../../06-operacao/resiliencia.md]
sources: [Dia 4 manhã notas 27-29 e 37, One-page Dia 4, Autoestudo Aula 2 nº 13, Autoestudo Aula 4 nº 6]
---

# ADR 0006 — Idempotência por `request_control_key`

> [Índice](../../README.md) › [Decisões](README.md) › 0006

**Status:** aceita

## Contexto

Quando o pedido estoura o timeout, quem chamou não sabe se a operação foi executada. Se tentar de novo, pode debitar duas vezes; se não tentar, a transferência pode ter ficado pela metade do ponto de vista do cliente. Na QI Tech, Pix, TED, cobrança e boleto usam o mesmo padrão: um `request_control_key` gerado por quem chama.

## Decisão

- `POST /account/{account_key}/transaction` exige `request_control_key` (UUID) **no corpo**, validado pelo schema.
- A coluna `transaction.request_control_key CHAR(36) UNIQUE` fica preenchida só na linha principal da operação (`DEPOSIT` ou `TRANSFER_OUT`). Nas demais é `NULL`, e o Postgres aceita vários `NULL` num índice `UNIQUE`.
- No controller, **antes** de travar as contas:
  1. O repository busca uma transação com essa chave.
  2. Se ela existe e o corpo bate (mesma conta, tipo, valor e destino), a resposta é **200 com o DTO original**, sem executar nada.
  3. Se ela existe e o corpo difere, a resposta é **409 `QIT002016`**.
- Corrida entre duas requisições com a mesma chave nova: a segunda falha no `UNIQUE` no commit. O controller captura o `IntegrityError` e repete o passo 1.
- A divisão de responsabilidades segue a aula: **a busca fica no repository, a decisão no controller, a garantia no banco**.

## Alternativas descartadas

- **Chave no header `Idempotency-Key`.**
  - **Preço:** o schema JSON não valida header, então a regra fica espalhada. O padrão interno da QI usa o campo no corpo.
  - **Ganharia se** a API seguisse o rascunho IETF, como fazem gateways públicos (Stripe).
- **Tabela separada `idempotency` com a resposta serializada.**
  - **Preço:** mais uma escrita por pedido, e uma resposta guardada pode ficar desatualizada em relação ao DTO.
  - **Ganharia se** várias rotas de tipos diferentes precisassem de idempotência.
- **Deduplicar por (conta, valor, janela de tempo).**
  - **Preço:** duas transferências legítimas e iguais seguidas seriam bloqueadas.
- **Não fazer nada.**
  - **Preço:** um retry depois de timeout debita em dobro.

## Consequências

- Retentar com a mesma chave é sempre seguro para quem chama.
- O depósito também é idempotente, porque usa a mesma rota e a mesma regra.
