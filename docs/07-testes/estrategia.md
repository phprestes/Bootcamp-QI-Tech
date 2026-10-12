---
title: Estratégia de testes
summary: Testes black box por HTTP (R1), ciclo TDD, padrão prepara-age-confere, Mockserver para o birô, helpers em tests/utils e como rodar.
related: [../01-contexto/requisitos.md, ../06-operacao/rodando-localmente.md, ../06-operacao/resiliencia.md]
sources: [Aula 3 tarde (TDD na QI Tech), Guia Dia 3, Autoestudo Aula 3, bootcamp-base-api tests/, biblioteca-api tests/]
---

# Estratégia de testes

> [Índice](../README.md) › Testes › Estratégia
>
> **Responde a:** que tipo de teste escrevemos? como simular o birô? onde fica cada helper? como rodar?

## Black box primeiro

O teste fala com a API **só por HTTP**, como o cliente real, e confere **status e corpo**. **Nenhum arquivo em `tests/` importa nada de `src/`** e nenhum lê o banco (R1). Quando o teste importa `src/`, ele deixou de ser black box.

| | Unitário | Black box (padrão) |
|---|---|---|
| Enxerga | uma função | a feature inteira: middleware → schema → controller → banco → DTO |
| Precisa de | Python | `docker compose up` |
| Sobrevive a refatoração | não | sim |
| Usar para | lógica pura isolada | **toda regra de negócio** |

Como R1 proíbe importar `src/`, mesmo a validação de CPF é provada pela API (`POST /customer` com dígito errado devolve 422).

## TDD

1. **Planejar.** Ler a regra na [matriz](../01-contexto/requisitos.md#matriz-regra--teste): o que a rota recebe, devolve e barra.
2. **Testar.** Escrever o teste antes do código.
3. **Falhar.** Ver o vermelho **pelo motivo certo**. Um teste que nunca falhou pode não testar nada.
4. **Implementar** o mínimo para ficar verde e refatorar com o verde.

Regras:

- Nenhuma linha nova em `src/` sem um teste vermelho pedindo por ela.
- **Cada `if` do controller tem pelo menos dois testes**: o que passa e o que é barrado.

## Anatomia de um teste: prepara, age, confere

```python
class TestTransfer:
    def test_transfer_without_balance_returns_422_and_keeps_both_balances(self):
        """RN14: saldo menor que valor + tarifa não move dinheiro em nenhuma conta."""
        origin = ObjectGenerator.create_account_with_balance(10000)
        destination = ObjectGenerator.create_account()

        status, body = RequestGenerator.POST_transaction(
            origin["account_key"],
            PayloadGenerator.create_transfer_payload(destination["account_key"], amount=10000),
        )

        assert status == 422
        assert body["code"] == "QIT002012"
        assert RequestGenerator.GET_account(origin["account_key"])[1]["balance"] == 10000
        assert RequestGenerator.GET_account(destination["account_key"])[1]["balance"] == 0
```

- **Preparar pela porta da frente.** Para ter um cliente, faça `POST /customer`, nunca `INSERT`.
- **Cada teste cria o próprio mundo**, com CPF e keys novas, e não depende da ordem dos outros.
- **O nome diz o comportamento garantido**: `test_<ação>_<cenário>_returns_<status>`. A docstring cita a regra (RN/R).
- **Conferir status e corpo**, incluindo `code` e o formato `{title, description, translation, code}`.

## Mockserver no lugar do birô

O connector lê `BUREAU_API_URL` do ambiente. No compose, ela aponta para `http://mock:1080/bureau`, sem nenhuma linha de `src/` mudar. Ritual de cada teste que envolve o birô:

1. Ensinar a resposta (*expectation*): `REGULAR`, `SUSPENDED`, `404`, `500`, ou `delay` maior que o timeout.
2. Chamar a API pela porta da frente.
3. Conferir status e corpo.
4. *Verify*: o birô foi chamado? Quantas vezes? Com o `INTERNAL-TOKEN` dele? Nos casos 409 e 422 locais, conferir que **não** foi chamado.

Regra: **o Mockserver substitui só quem está fora da API.** O banco e as camadas rodam de verdade.

## Helpers (`tests/utils/`)

| Arquivo | Papel |
|---|---|
| `requisition.py` | Monta a URL base (`SERVER_LOCALHOST`, `API_PORT`) e envia |
| `request_generator.py` | `POST_customer`, `GET_account`, `POST_transaction`… põem o `INTERNAL-TOKEN` e devolvem `(status, json)` |
| `payload_generator.py` | Payload válido com campos sobrescrevíveis (`**overrides`) |
| `object_generator.py` | Cria entidades prontas via API (cliente, conta, conta com saldo) |
| `random_generator.py` | CPF válido aleatório, UUID |
| `mock_utils.py` | Cliente do Mockserver: `clear`, `add_expectations`, `retrieve_requests`, `verify` |
| `mock_generator.py` | `BureauMock`: `regular`, `suspended`, `not_found`, `server_error(times=)`, `unexpected_body`, `connection_dropped`, `slower_than_timeout`, `received_calls`. Cada expectation vale para um CPF, então os testes não se atrapalham |
| `db_utils.py` | Recria o schema. Usar só em teste que conta linhas globais |


## Organização

```
tests/
├── conftest.py
├── integration/
│   ├── test_healthcheck.py      # rotas abertas, 403 sem token, 404 de rota
│   ├── customer/   test_customer_create.py  test_customer_get.py
│   ├── account/    test_account_create.py   test_account_status.py
│   └── transaction/ test_deposit.py test_transfer.py test_statement.py test_idempotency.py test_concurrency.py
└── utils/
```

## Como rodar

```bash
make up test                                     # ou: docker compose up -d --wait && pytest -v
pytest tests/integration/transaction -v          # só uma pasta
pytest -k insufficient -v                        # por nome
pytest --cov                                     # cobertura (pytest-cov)
```
