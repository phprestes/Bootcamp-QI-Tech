---
title: O problema
summary: O que o banco digital oferece, quem usa, que garantias dá sobre o dinheiro e o que fica fora do escopo.
related: [requisitos.md, ../02-arquitetura/visao-geral.md, ../rfc/RFC.md]
sources: [Aula 1 tarde ("É construir um banco!"), Aula 2 (modelo de RFC), Aula 3 tarde p.18]
---

# O problema

> [Índice](../README.md) › Contexto › Problema
>
> **Responde a:** o que o sistema faz? por que isso é difícil? o que não entra?

## O que o sistema oferece

O desafio do bootcamp é construir um banco com cinco capacidades:

1. **Cadastro de cliente.** O CPF precisa ser válido, único e regular no birô.
2. **Conta vinculada a um cliente.** Toda conta tem estado e saldo.
3. **Transação com controle de saldo.** Cobre depósito e transferência entre contas.
4. **Tarifa na transferência.** É cobrada da conta de origem no mesmo ato.
5. **Extrato paginado.** É a lista das transações de uma conta.

Quem chama o serviço são outros sistemas internos, identificados pelo cabeçalho `INTERNAL-TOKEN`. O sistema não tem interface de usuário.

## As garantias sobre o dinheiro

| Garantia | O que acontece se falhar |
|---|---|
| **Saldo nunca fica negativo**, mesmo com dois débitos simultâneos na mesma conta | O banco empresta dinheiro que não tem, e o saldo diverge da realidade. |
| **Transferência é tudo ou nada**: débito, crédito e tarifa entram juntos | O dinheiro sai de uma conta e não chega na outra, ou a tarifa some. |
| **Pedido repetido não executa duas vezes** | Um retry após timeout debita o cliente em dobro. |
| **Nada que entrou deixa de existir** | O extrato deixa de reconstruir o saldo e a auditoria perde o rastro. |
| **Dinheiro é exato** (inteiro em centavos) | Erros de arredondamento de float acumulam centavos fantasmas. |

## Por que é difícil

O caminho feliz é trivial. Os casos difíceis são três:

- **Concorrência sobre o mesmo saldo.** Duas transferências leem R$ 100 ao mesmo tempo e as duas debitam.
- **Repetição.** O cliente não sabe se a primeira tentativa passou.
- **A dependência externa (birô)** pode demorar ou estar fora do ar.

Ver [transferência](../05-fluxos/transferencia.md) e [resiliência](../06-operacao/resiliencia.md).

## Fora do escopo desta entrega

- Saque, boleto, Pix e TED.
- Estorno ou cancelamento de transação, já que a correção seria uma transação nova.
- Edição e exclusão de cliente.
- Autenticação de usuário final, porque quem chama são sistemas internos.
- Multi-moeda.
- Limite de crédito ou cheque especial.
- Juros.
- Notificação a terceiros.
