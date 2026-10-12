---
title: "ADR 0009: Contrato de entrada em JSON Schema"
summary: O formato de corpo e query string é declarado em JSON Schema fechado (additionalProperties false), não em modelos Pydantic.
related: [../camadas.md, ../../03-api/convencoes.md, ../../06-operacao/seguranca.md]
sources: [bootcamp-base-api (SchemaHandler), Autoestudo Aula 3 (camada de contrato), Aula 2 manhã (schema / DTO)]
---

# ADR 0009: Contrato de entrada em JSON Schema

> [Índice](../../README.md) › [Decisões](README.md) › 0009

**Status:** aceita

## Contexto

Toda rota precisa recusar com 400 o que chega na forma errada antes de qualquer regra rodar. O FastAPI oferece Pydantic para isso; o serviço-base da aula já traz o `SchemaHandler`, que valida com `jsonschema` os arquivos de `src/schemas/`.

## Decisão

- Cada rota com corpo ou query string tem um arquivo em `src/schemas/`, aplicado pelo decorator `@SchemaHandler.validate(...)`.
- Todo schema usa `additionalProperties: false`: campo ou parâmetro desconhecido é recusado, não ignorado.
- O schema confere só formato. Dígito verificador, idade, saldo e estado são regras do controller.

## Alternativas descartadas

- **Modelos Pydantic na assinatura da rota.**
  - **Preço:** o contrato fica preso ao Python, e quem integra precisa ler o código ou o OpenAPI gerado, que está desligado.
  - **Ganharia se** o time fosse só Python, sem integradores externos, e quisesse autocompletar no corpo.
- **Validar à mão no resource.**
  - **Preço:** `if` de formato espalhado pelas rotas, mensagens diferentes para o mesmo erro e campo a mais aceito em silêncio.
  - **Ganharia se** houvesse uma única rota com um único campo.

## Consequências

- O corpo chega ao controller como `dict`, sem tipos nem autocompletar.
- O contrato é um arquivo que quem integra lê sem abrir o código, no mesmo formato dos serviços da QI Tech.
- Campo a mais vira `400 QIT000001`, o que barra *mass assignment* (mandar `balance` no corpo).
