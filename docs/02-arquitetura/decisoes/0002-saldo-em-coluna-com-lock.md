---
title: "ADR 0002: Saldo em coluna, com lock pessimista e CHECK"
summary: account.balance guarda o saldo; toda escrita trava as contas com SELECT … FOR UPDATE em ordem de id; o banco recusa saldo negativo.
related: [../../05-fluxos/transferencia.md, ../../04-dados/modelo.md, 0003-transacao-tabela-unica-com-tipo.md]
sources: [Aula 2 tarde p.32-37 (ACID, FOR UPDATE), Autoestudo Aula 2 nº 12 (concorrência), 'Aula 2 p.59 ("onde mora o saldo?")']
---

# ADR 0002: Saldo em coluna, com lock pessimista e CHECK

> [Índice](../../README.md) › [Decisões](README.md) › 0002

**Status:** aceita

## Contexto

O cenário clássico é o *lost update*: duas transferências leem o mesmo saldo de R$ 100 e as duas debitam R$ 80. A aula perguntou onde mora o saldo, numa coluna ou na soma das transações, e listou três saídas para a concorrência: lock pessimista, versão otimista ou deixar o banco decidir.

## Decisão

- `account.balance BIGINT NOT NULL DEFAULT 0` com `CONSTRAINT balance_non_negative CHECK (balance >= 0)`.
- Toda operação que muda saldo:
  1. Abre a transação, que já é implícita na sessão da requisição.
  2. Carrega as contas envolvidas com `with_for_update()`, sempre em ordem crescente de `id`. Essa ordem fixa evita deadlock quando A→B e B→A acontecem juntos.
  3. Valida o estado e o saldo depois do lock.
  4. Grava as transações (append-only) e atualiza `balance`.
  5. Faz um `commit` no controller. Se qualquer passo falhar, o middleware faz rollback.
- O `CHECK` é a segunda rede de proteção. Se um bug passar pela validação, o banco recusa o resultado e a resposta é 500, com log.
- O extrato reconstrói o saldo: `SUM(créditos) - SUM(débitos) = balance`. Há um teste que confere essa igualdade.

## Alternativas descartadas

- **Saldo = soma das transações, sem coluna.**
  - **Preço:** cada leitura de saldo varre o histórico inteiro. Para validar saldo sob concorrência ainda é preciso travar algo, a conta ou um advisory lock, então o lock não some.
  - **Ganharia se** o volume fosse baixo e houvesse snapshots periódicos.
- **Lock otimista (coluna `version`).**
  - **Preço:** quando há conflito, o pedido falha e o cliente precisa reenviar. Contas muito movimentadas viram uma fila de 409.
  - **Ganharia se** os conflitos fossem raros e o tempo de lock fosse crítico.
- **Só o banco decide (`UPDATE … SET balance = balance - :v WHERE balance >= :v RETURNING`).**
  - **Preço:** funciona bem para uma conta, mas a transferência mexe em duas contas mais a tarifa e ainda precisa ler o estado da conta. A lógica acaba espalhada entre SQL e controller.
  - **Ganharia se** a operação fosse um débito simples numa conta só.
- **Não fazer nada (ler, calcular e gravar sem lock).**
  - **Preço:** saldo negativo ou divergente sob carga. O `CHECK` barraria o negativo com um 500, mas não o lost update entre saldos positivos.

## Consequências

- Transferências na mesma conta são serializadas. É aceitável, porque o lock dura milissegundos e nenhuma chamada HTTP acontece dentro dele.
- O teste de concorrência dispara N transferências em paralelo e confere que o saldo final é igual à soma do extrato e nunca fica negativo.
