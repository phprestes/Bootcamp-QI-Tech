---
title: Requisitos, regras de negócio e matriz regra → teste
summary: Restrições R1–R8 do enunciado, regras de negócio do banco e o teste que prova cada uma.
related: [problema.md, ../03-api/erros.md, ../07-testes/estrategia.md]
sources: [Autoestudo Aula 2 (R3–R8), Autoestudo Aula 3 (R1, R2), Aula 3 tarde p.18, Aula 1 tarde, One-page Dia 4]
---

# Requisitos

> [Índice](../README.md) › Contexto › Requisitos
>
> **Responde a:** o que a banca cobra? quais regras o sistema impõe? qual teste prova cada regra?

## Restrições do enunciado (R1–R8)

São parte do enunciado do desafio e cobradas pela banca. A coluna do meio aponta onde o material das aulas trata cada uma.

| # | Restrição | Onde o material cita | Como o projeto atende |
|---|---|---|---|
| R1 | Nenhum arquivo de teste importa código de dentro da aplicação | Autoestudo 3 (teste black box) | Os testes usam só HTTP. Ver [estratégia de testes](../07-testes/estrategia.md). |
| R2 | A entrega sobe e roda com um comando na máquina limpa do avaliador (Linux) | Autoestudo 3; Dia 3 manhã p.33; Dia 4 tarde | `make all` (ou `docker compose up -d --wait` e `pytest`). Ver [rodando localmente](../06-operacao/rodando-localmente.md). |
| R3 | Erro não é só status: o corpo traz um código próprio | Autoestudo 2 ("Designing API Errors") | Corpo `{title, description, translation, code}`. Ver [erros](../03-api/erros.md). |
| R4 | **Nada que entrou deixa de existir** (append-only; soft delete não serve) | Autoestudo 2 | `transaction` e `account_status_event` só recebem INSERT. Ver [modelo](../04-dados/modelo.md). |
| R5 | Nenhum identificador devolvido é o número que o banco gerou | Autoestudo 2 | `<entidade>_key` UUID. Ver [ADR 0005](../02-arquitetura/decisoes/0005-uuid-key-publica.md). |
| R6 | Dinheiro não é float | Autoestudo 2 ("FLOAT pra dinheiro") | `BIGINT` em centavos. Ver [ADR 0004](../02-arquitetura/decisoes/0004-dinheiro-em-centavos.md). |
| R7 | A RFC registra as decisões tomadas e as descartadas, com o preço de cada uma | Modelo de RFC; Autoestudo 2 | [ADRs](../02-arquitetura/decisoes/README.md) e [RFC](../rfc/RFC.md). |
| R8 | Recurso de outro dono responde 404, não 403 (autorização, não só autenticação) | Autoestudo 2 (IDOR) | Toda busca aninhada filtra pelo pai. Ver [segurança](../06-operacao/seguranca.md). |

## Regras de negócio

| ID | Regra | Recusa |
|---|---|---|
| RN01 | O CPF precisa ter formato `000.000.000-00` | 400 `QIT000001` |
| RN02 | Os dígitos verificadores do CPF precisam bater | 422 `QIT002003` |
| RN03 | O CPF é único entre clientes | 409 `QIT002002` |
| RN04 | O cliente precisa ter 18 anos ou mais | 422 `QIT002004` |
| RN04a | A data de nascimento precisa existir e estar no passado (`1990-02-30` não existe) | 422 `QIT002017` |
| RN05 | O CPF precisa estar `REGULAR` no birô | 422 `QIT002005` |
| RN06 | Birô fora do ar, lento ou com resposta inesperada | 502 `QIT002006` |
| RN07 | Conta só é aberta para cliente existente | 404 `QIT002001` |
| RN08 | O cliente pode ter no máximo `MAX_ACCOUNTS_PER_CUSTOMER` (padrão 3) contas não encerradas | 409 `QIT002008` |
| RN09 | A conta nasce `ACTIVE`, com saldo 0, e o evento é registrado | — |
| RN10 | Transições válidas: `ACTIVE ⇄ BLOCKED` e `ACTIVE → CLOSED`. `CLOSED` é final | 409 `QIT002010` |
| RN11 | Só fecha conta com saldo 0 | 409 `QIT002011` |
| RN12 | Só movimenta conta `ACTIVE` (origem e destino) | 409 `QIT002009` |
| RN13 | Valor inteiro em centavos, `>= 1` | 400 `QIT000001` |
| RN14 | Transferência precisa de saldo para valor + tarifa. Se não houver, nenhum saldo muda | 422 `QIT002012` |
| RN15 | Não se transfere para a mesma conta | 422 `QIT002013` |
| RN16 | A conta de destino precisa existir | 404 `QIT002014` |
| RN17 | A tarifa `TRANSFER_FEE_CENTS` (padrão 200) é debitada da origem na mesma transação ACID | — |
| RN18 | Mesma `request_control_key` com o mesmo corpo devolve a resposta original, sem executar de novo | 200 (resposta original) |
| RN19 | Mesma `request_control_key` com corpo diferente é recusada | 409 `QIT002016` |
| RN20 | Transação de outra conta não aparece | 404 `QIT002015` (R8) |
| RN21 | Extrato paginado: `limit` 1–100 (padrão 10), `page >= 0` (padrão 0) | 400 `QIT000001` |
| RN22 | Toda rota, exceto `/` e `/health_check`, exige `INTERNAL-TOKEN` | 403 `QIT000002` |

## Matriz regra → teste

Pela regra do TDD da aula, cada `if` tem pelo menos dois testes: o caminho que passa pela regra e o caminho barrado por ela. Os arquivos ficam em `tests/integration/<recurso>/`; a docstring de cada teste cita a regra.

| Regra | Teste que passa | Teste barrado | Arquivo |
|---|---|---|---|
| RN01 | `test_post_customer_returns_201_with_key` | `test_post_customer_with_unmasked_cpf_returns_400`, `test_post_customer_with_unknown_field_returns_400` | `customer/test_customer_create.py` |
| RN02 | `test_post_customer_returns_201_with_key` | `test_post_customer_with_invalid_cpf_returns_422` | idem |
| RN03 | `test_post_customer_returns_201_with_key` | `test_post_customer_with_duplicate_cpf_returns_409` | idem |
| RN04 / RN04a | `test_post_customer_adult_returns_201` | `test_post_customer_underage_returns_422`, `test_post_customer_with_impossible_date_returns_422` | idem |
| RN05 | `test_post_customer_calls_bureau_once_with_its_token` | `test_post_customer_suspended_cpf_returns_422`, `test_post_customer_unknown_to_bureau_returns_422` | idem |
| RN06 | `test_post_customer_after_bureau_failure_can_be_retried` | `test_post_customer_bureau_down_returns_502`, `test_post_customer_bureau_timeout_returns_502`, `test_post_customer_bureau_connection_dropped_returns_502`, `test_post_customer_bureau_unexpected_body_returns_502` | idem |
| RN07 | `test_post_account_returns_201_active_zero_balance` | `test_post_account_unknown_customer_returns_404` | `account/test_account_create.py` |
| RN08 | `test_post_account_up_to_limit_returns_201`, `test_closed_account_frees_a_slot` | `test_post_account_over_limit_returns_409` | idem |
| RN09 | `test_post_account_returns_201_active_zero_balance`, `test_new_account_history_starts_at_opening` | — | idem |
| RN10 | `test_put_account_status_block_and_unblock` | `test_put_account_status_closed_is_final_returns_409`, `test_put_account_status_same_status_returns_409`, `test_close_blocked_account_returns_409` | `account/test_account_status.py` |
| RN11 | `test_put_account_status_close_with_zero_balance_returns_200` | `test_close_account_with_balance_returns_409` | idem |
| RN12 | `test_deposit_on_active_account_returns_201` | `test_deposit_on_blocked_account_returns_409`, `test_deposit_on_closed_account_returns_409`, `test_transfer_from_blocked_account_returns_409`, `test_transfer_to_closed_account_returns_409` | `transaction/test_deposit.py`, `transaction/test_transfer.py` |
| RN13 / R6 | `test_deposit_on_active_account_returns_201` | `test_deposit_with_zero_amount_returns_400`, `test_deposit_with_decimal_amount_returns_400` | `transaction/test_deposit.py` |
| RN14 | `test_transfer_debits_amount_plus_fee_and_credits_destination`, `test_transfer_of_exact_balance_minus_fee_leaves_zero` | `test_transfer_without_balance_returns_422_and_keeps_both_balances` | `transaction/test_transfer.py` |
| RN15 | — | `test_transfer_to_same_account_returns_422` | idem |
| RN16 | — | `test_transfer_to_unknown_account_returns_404` | idem |
| RN17 | `test_transfer_debits_amount_plus_fee_and_credits_destination`, `test_transfer_is_visible_in_both_statements` | — | idem |
| RN18 | `test_repeated_request_control_key_returns_same_transaction`, `test_repeated_deposit_is_credited_once` | — | `transaction/test_idempotency.py` |
| RN19 | — | `test_reused_request_control_key_with_other_amount_returns_409`, `test_reused_request_control_key_on_other_account_returns_409` | idem |
| RN20 / R8 | `test_get_transaction_of_own_account_returns_200`, `test_get_customer_accounts_lists_only_own_accounts` | `test_get_transaction_of_other_account_returns_404` | `transaction/test_statement.py`, `customer/test_customer_get.py` |
| RN21 | `test_statement_pagination_envelope`, `test_get_customers_pagination_envelope` | `test_statement_limit_over_100_returns_400`, `test_statement_limit_zero_returns_400`, `test_get_customers_with_unknown_param_returns_400` | idem |
| RN22 | `test_home`, `test_health_check` (rotas abertas) | `test_no_token` | `test_healthcheck.py` |
| R4 | `test_statement_rebuilds_balance` | — | `transaction/test_statement.py` |
| R5 | `test_get_customer_returns_200` (sem `id` nem `*_id` na resposta) | — | `customer/test_customer_get.py` |
| Concorrência | `test_crossed_transfers_do_not_deadlock` | `test_concurrent_transfers_never_make_balance_negative` | `transaction/test_concurrency.py` |

O teste de concorrência foi validado por mutação: sem a trava em `TransactionController._transfer`, ele fica vermelho (saque a descoberto e *lost update*).
