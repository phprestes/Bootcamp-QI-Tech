---
title: Convenções da API
summary: Regras REST, status HTTP, formato de erro, paginação, filtros, headers e autenticação que toda rota segue.
related: [rotas.md, erros.md, ../02-arquitetura/decisoes/0007-convencao-de-rotas.md]
sources: [Aula 2 manhã p.16-27, Aula 3 manhã p.7, bootcamp-base-api, RFC 9110]
---

# Convenções da API

> [Índice](../README.md) › API › Convenções
>
> **Responde a:** como nomear uma rota? qual status devolver? como paginar? que headers são obrigatórios?

## REST

- **O endereço nomeia a coisa e o método diz a ação.** `POST /customer`, nunca `/createCustomer`.
- **GET nunca muda estado.**
- **Em dinheiro não existe DELETE.** Encerrar é mudar o estado (`PUT /account/{key}/status`).
- **Filtro, ordenação e paginação vão na query string**, nunca no path.
- **A `_key` UUID é o identificador que aparece fora da API.** O `id` não sai. Ver [ADR 0005](../02-arquitetura/decisoes/0005-uuid-key-publica.md).
- **Item no singular e lista no plural**, sem versão na URL. Ver [ADR 0007](../02-arquitetura/decisoes/0007-convencao-de-rotas.md).
- Campos e path em `snake_case`, em inglês. A prosa e os textos de erro (`translation`) ficam em português.

## Métodos

| Método | Uso aqui | Sucesso |
|---|---|---|
| `GET` | ler item ou lista | `200` |
| `POST` | criar (cliente, conta, transação) | `201` + `{<recurso>_key, …}`; repetição idempotente: `200` |
| `PUT` | trocar o estado de um sub-recurso (`/status`) | `200` |
| `PATCH`, `DELETE` | não usados | — |

## Status HTTP

A régua das aulas:

- **2xx** é o caminho desenhado.
- **4xx** é uma exceção que nós desenhamos.
- **5xx** é um ramo que faltou no fluxo, com uma exceção: o `502` é desenhado de propósito.

| Status | Quando |
|---|---|
| `200` | Leitura, mudança de estado, ou repetição idempotente |
| `201` | Recurso criado |
| `204` | `GET /health_check` |
| `400` | Corpo ou query fora do schema (`QIT000001`), ou parâmetros contraditórios (`QIT000010`) |
| `403` | `INTERNAL-TOKEN` ausente ou errado (`QIT000002`) |
| `404` | Key inexistente **ou de outro dono** (R8), e rota inexistente (`QIT000404`) |
| `405` | Método não aceito na rota (`QIT000405`) |
| `409` | Conflito de estado: duplicado, transição inválida, conta não ativa, chave de idempotência reutilizada |
| `422` | O formato está certo, mas o valor não pode existir: CPF com dígito errado, menor de idade, saldo insuficiente, CPF irregular |
| `502` | Birô fora do ar, lento ou com resposta inesperada |
| `500` | Erro não previsto (`QIT000500`). Cada ocorrência é um bug a nomear |

> **Nunca devolva `200` com erro no corpo.** E nunca invente campo `success`: a faixa do status já diz o resultado.

## Formato de erro (R3)

Toda recusa tem o mesmo corpo:

```json
{
  "title": "Insufficient Balance",
  "description": "Origin account balance does not cover amount plus fee.",
  "translation": "Saldo insuficiente para o valor mais a tarifa.",
  "code": "QIT002012"
}
```

Cada recusa é uma classe em `src/errors/custom_errors.py`. O `error_verification()` derruba a API no boot se dois erros compartilharem um código. O catálogo completo está em [erros.md](erros.md).

## Paginação e filtros

- Query: `limit` (1–100, padrão 10) e `page` (≥ 0, padrão 0). Um parâmetro desconhecido devolve 400.
- Resposta:

  ```json
  { "data": [ … ], "limit": 10, "page": 0, "is_last_page": false }
  ```

- O repository busca `limit + 1` linhas para saber se existe próxima página e ordena por `created_at DESC, id DESC`.
- Filtros são opcionais e vão na query. Exemplos: `GET /customers?document_number=…` e `GET /account/{key}/transactions?type=FEE`.
- Listagens trazem a versão simplificada do DTO, sem o histórico de eventos.

## Headers

| Header | Direção | Regra |
|---|---|---|
| `INTERNAL-TOKEN` | entrada | Obrigatório, exceto em `/` e `/health_check`. O valor vem da variável de ambiente `INTERNAL_TOKEN` |
| `X-Request-ID` | entrada/saída | Opcional na entrada (`[A-Za-z0-9_-]{1,64}`). Se faltar, é gerado. Sempre volta na resposta e em toda linha de log |
| `Content-Type` | entrada | `application/json` |

## Contrato de entrada × saída

- **Entrada:** JSON Schema em `src/schemas/<verbo>_<recurso>.json`, com `additionalProperties: false`. O schema confere **formato**, não verdade: dígito verificador e saldo são assunto do controller.
- **Saída:** um DTO por recurso em `src/dtos/`. O DTO escolhe o nome de cada campo e nunca expõe `id`.
