---
title: "ADR 0004: Dinheiro em BIGINT de centavos"
summary: Todo valor monetário é inteiro em centavos no banco, na API e nos testes; nunca float (R6).
related: [../../03-api/convencoes.md, ../../04-dados/modelo.md]
sources: [Autoestudo Aula 2 nº 10 (centavos × decimal × float), Aula 2 p.40 (balance BIGINT)]
---

# ADR 0004: Dinheiro em `BIGINT` de centavos

> [Índice](../../README.md) › [Decisões](README.md) › 0004

**Status:** aceita

## Contexto

`0.1 + 0.2 != 0.3` em ponto flutuante. Em dinheiro, esse erro acumula centavos que não existem (R6).

## Decisão

- **Banco:** `BIGINT` em centavos, nas colunas `balance` e `amount`.
- **API:** inteiro em centavos, com campo nomeado de forma explícita: `amount` e `balance` são sempre centavos. A documentação e os exemplos deixam isso claro (`"amount": 20000` equivale a R$ 200,00).
- **Schema:** `"type": "integer", "minimum": 1`. Se chegar um decimal, a resposta é 400.
- Moeda única, BRL. Por isso não existe coluna de moeda.

## Alternativas descartadas

- **`NUMERIC(15,2)` + `Decimal` no Python.**
  - **Preço:** exige disciplina para nunca converter para float, e o JSON serializa como string ou float conforme a biblioteca.
  - **Ganharia se** fosse preciso guardar frações de centavo, como juros diários ou câmbio.
- **`FLOAT`/`REAL`.**
  - **Preço:** erro de arredondamento. Descartado sem discussão (R6).
- **String `"200.00"` na API.**
  - **Preço:** o cliente precisa fazer parse, e a validação passa a depender de regex.
  - **Ganharia se** a API fosse pública e consumida por front-ends que exibem o valor direto.

## Consequências

- Nenhum cálculo do controller usa float.
- A formatação para reais é responsabilidade de quem consome a API.
