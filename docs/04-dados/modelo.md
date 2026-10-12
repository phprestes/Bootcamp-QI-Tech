---
title: Modelo de dados
summary: Diagrama ER e DDL de referência das tabelas customer, account, account_status, account_status_event, transaction e transaction_type.
related: [estados.md, ../02-arquitetura/decisoes/0002-saldo-em-coluna-com-lock.md, ../02-arquitetura/decisoes/0003-transacao-tabela-unica-com-tipo.md]
sources: [Aula 2 tarde p.32-45, Aula 3 manhã p.8, database.sql do base-service e da biblioteca]
---

# Modelo de dados

> [Índice](../README.md) › Dados › Modelo
>
> **Responde a:** quais tabelas existem? o que garante unicidade? onde mora o saldo? o que é append-only?

O schema mora em `database/database.sql` e só roda quando o banco nasce: depois de mudá-lo, `make reset` ([rodando localmente](../06-operacao/rodando-localmente.md)).

## Diagrama

```mermaid
erDiagram
    CUSTOMER ||--o{ ACCOUNT : "possui"
    ACCOUNT_STATUS ||--o{ ACCOUNT : "estado atual"
    ACCOUNT ||--o{ ACCOUNT_STATUS_EVENT : "histórico"
    ACCOUNT ||--o{ TRANSACTION : "lançamentos"
    TRANSACTION_TYPE ||--o{ TRANSACTION : "classifica"
    TRANSACTION ||--o{ TRANSACTION : "origin_transaction_id"

    CUSTOMER {
        serial id PK
        char36 customer_key UK "sai na resposta"
        varchar255 name
        char14 document_number UK "CPF com máscara"
        date birthdate
        timestamptz created_at
    }
    ACCOUNT {
        serial id PK
        char36 account_key UK "sai na resposta"
        int customer_id FK
        int status_id FK
        bigint balance "centavos, CHECK >= 0"
        timestamptz created_at
        timestamptz updated_at
    }
    ACCOUNT_STATUS {
        serial id PK
        varchar20 enumerator UK "ACTIVE, BLOCKED, CLOSED"
    }
    ACCOUNT_STATUS_EVENT {
        serial id PK
        int account_id FK
        int from_status_id FK "NULL na abertura"
        int to_status_id FK
        varchar255 reason
        timestamptz created_at "quando aconteceu"
    }
    TRANSACTION_TYPE {
        serial id PK
        varchar20 enumerator UK "DEPOSIT, TRANSFER_OUT, TRANSFER_IN, FEE"
    }
    TRANSACTION {
        serial id PK
        char36 transaction_key UK "sai na resposta"
        int account_id FK "conta afetada pela linha"
        int type_id FK
        bigint amount "centavos, CHECK > 0"
        int counterpart_account_id FK "outra ponta, NULL em DEPOSIT"
        int origin_transaction_id FK "IN e FEE apontam para OUT"
        char36 request_control_key UK "idempotência, só na linha principal"
        timestamptz created_at
    }
```

## DDL

Cópia fiel de [`database/database.sql`](../../database/database.sql), que é a fonte; atualize os dois juntos.

```sql
-- Roda só quando o volume do banco nasce: depois de mudar este arquivo, `make reset`.
-- Desenho e invariantes: docs/04-dados/modelo.md.

CREATE TABLE customer(
    id                              SERIAL PRIMARY KEY,
    customer_key                    CHAR(36) NOT NULL,
    name                            VARCHAR(255) NOT NULL,
    document_number                 CHAR(14) NOT NULL,
    birthdate                       DATE NOT NULL,
    created_at                      TIMESTAMPTZ NOT NULL DEFAULT(NOW()),
    UNIQUE(customer_key),
    UNIQUE(document_number)
);

CREATE TABLE account_status(
    id                              SERIAL PRIMARY KEY,
    enumerator                      VARCHAR(20) NOT NULL,
    created_at                      TIMESTAMPTZ NOT NULL DEFAULT(NOW()),
    UNIQUE(enumerator)
);

INSERT INTO account_status (enumerator) VALUES
('ACTIVE'),
('BLOCKED'),
('CLOSED');

CREATE TABLE account(
    id                              SERIAL PRIMARY KEY,
    account_key                     CHAR(36) NOT NULL,
    customer_id                     INTEGER NOT NULL REFERENCES customer(id),
    status_id                       INTEGER NOT NULL REFERENCES account_status(id),
    -- Centavos (R6). O CHECK é a última rede: o controller já valida com a conta travada.
    balance                         BIGINT NOT NULL DEFAULT 0,
    created_at                      TIMESTAMPTZ NOT NULL DEFAULT(NOW()),
    updated_at                      TIMESTAMPTZ NOT NULL DEFAULT(NOW()),
    UNIQUE(account_key),
    CONSTRAINT balance_non_negative CHECK (balance >= 0)
);

CREATE INDEX account_customer_id_idx ON account(customer_id);

-- Append-only (R4): uma linha por mudança de estado, inclusive a abertura (from_status_id NULL).
CREATE TABLE account_status_event(
    id                              SERIAL PRIMARY KEY,
    account_id                      INTEGER NOT NULL REFERENCES account(id),
    from_status_id                  INTEGER REFERENCES account_status(id),
    to_status_id                    INTEGER NOT NULL REFERENCES account_status(id),
    reason                          VARCHAR(255),
    created_at                      TIMESTAMPTZ NOT NULL DEFAULT(NOW())
);

CREATE INDEX account_status_event_account_id_idx ON account_status_event(account_id);

CREATE TABLE transaction_type(
    id                              SERIAL PRIMARY KEY,
    enumerator                      VARCHAR(20) NOT NULL,
    created_at                      TIMESTAMPTZ NOT NULL DEFAULT(NOW()),
    UNIQUE(enumerator)
);

INSERT INTO transaction_type (enumerator) VALUES
('DEPOSIT'),
('TRANSFER_OUT'),
('TRANSFER_IN'),
('FEE');

-- Append-only (R4): uma linha por conta afetada; o tipo define o sinal (docs/02-arquitetura/decisoes/0003-transacao-tabela-unica-com-tipo.md).
CREATE TABLE transaction(
    id                              SERIAL PRIMARY KEY,
    transaction_key                 CHAR(36) NOT NULL,
    account_id                      INTEGER NOT NULL REFERENCES account(id),
    type_id                         INTEGER NOT NULL REFERENCES transaction_type(id),
    amount                          BIGINT NOT NULL,
    counterpart_account_id          INTEGER REFERENCES account(id),
    origin_transaction_id           INTEGER REFERENCES transaction(id),
    -- Só a linha principal da operação carrega a chave; NULL repetido não fere o UNIQUE.
    request_control_key             CHAR(36),
    created_at                      TIMESTAMPTZ NOT NULL DEFAULT(NOW()),
    UNIQUE(transaction_key),
    UNIQUE(request_control_key),
    CONSTRAINT amount_positive CHECK (amount > 0)
);

CREATE INDEX transaction_statement_idx ON transaction(account_id, created_at DESC, id DESC);
```

## Invariantes

| Invariante | Quem garante |
|---|---|
| CPF único | `UNIQUE(document_number)` mais a checagem prévia no controller, para devolver 409 limpo |
| Saldo nunca negativo | `CHECK (balance >= 0)` mais o lock e a validação no controller ([ADR 0002](../02-arquitetura/decisoes/0002-saldo-em-coluna-com-lock.md)) |
| `balance = Σ créditos − Σ débitos` | Saldo e lançamentos gravados na mesma transação; conferido por teste |
| Pedido não executa duas vezes | `UNIQUE(request_control_key)` ([ADR 0006](../02-arquitetura/decisoes/0006-idempotencia-por-chave.md)) |
| Nada some (R4) | `transaction` e `account_status_event` só recebem `INSERT`, e nenhum repository tem `update`/`delete` para elas |
| Id interno não vaza (R5) | O DTO só serializa `*_key` |
