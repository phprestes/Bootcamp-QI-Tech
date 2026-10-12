---
title: Segurança
summary: INTERNAL-TOKEN, segredos em variável de ambiente, IDOR respondido com 404, validação de entrada e OWASP API Top 10 aplicado.
related: [observabilidade.md, ../03-api/convencoes.md, ../02-arquitetura/decisoes/0005-uuid-key-publica.md]
sources: [Dia 4 manhã notas 18-22, One-page Dia 4, Autoestudo Aula 2 nº 5 (IDOR), Autoestudo Aula 4 nº 7-9]
---

# Segurança

> [Índice](../README.md) › Operação › Segurança
>
> **Responde a:** quem pode chamar a API? onde ficam os segredos? como evitar que alguém veja o recurso de outro?

## Autenticação: `INTERNAL-TOKEN`

- É um middleware que confere o header `INTERNAL-TOKEN` contra a variável de ambiente `INTERNAL_TOKEN`.
- Se o header faltar ou não bater, a resposta é `403 QIT000002` e **o resource nunca roda**.
- As rotas abertas são `/` e `/health_check` (`BYPASS_ENDPOINTS`).
- O middleware **devolve** a resposta de erro em vez de levantar exceção, porque dentro de um middleware ninguém traduz a exceção.
- Em produção, cada serviço tem o próprio token, e só recebe o valor quem precisa chamar. O API Gateway é a única porta pública e autentica quem vem de fora com outra credencial. O `INTERNAL-TOKEN` nunca sai da rede interna.

## Segredos

- O **repositório é público na entrega**: um token no código passa a ser um token de todo mundo.
- Os valores reais ficam só em variáveis de ambiente (12-factor). O `.env` está no `.gitignore`; o `.env.example` tem só valores de exemplo.
- O padrão `default_token` serve para desenvolvimento. Em produção, a variável não pode ter padrão.

## Autorização e IDOR (R8)

A autenticação responde "quem é você?". A autorização responde "este recurso é seu?".

- Toda busca aninhada filtra pelo pai:
  - `GET /account/{a}/transaction/{t}` busca `WHERE transaction_key = :t AND account_id = :a.id`.
  - `GET /customer/{c}/accounts` filtra por `customer_id`.
- Um recurso que existe mas pertence a outro dono recebe **404, não 403**. O 403 confirmaria que o recurso existe.
- As keys são UUIDs ([ADR 0005](../02-arquitetura/decisoes/0005-uuid-key-publica.md)), o que impede enumeração.

## Entrada

- JSON Schema com `additionalProperties: false`, que barra *mass assignment*: campos como `balance` ou `status` no corpo são rejeitados.
- `X-Request-ID` é validado por regex com `fullmatch`, contra *log injection*.
- O SQL é sempre parametrizado (SQLAlchemy). Não existe SQL concatenado.

## OWASP API Security Top 10 (2023), aplicado

| Risco | Mitigação |
|---|---|
| API1 Broken Object Level Authorization | Filtro pelo pai + 404 (acima) |
| API2 Broken Authentication | Token obrigatório, comparado com o ambiente |
| API3 Broken Object Property Level Authorization | `additionalProperties: false` na entrada; o DTO escolhe a saída |
| API4 Unrestricted Resource Consumption | `limit ≤ 100` na paginação; timeout nos connectors |
| API8 Security Misconfiguration | `/docs` e `/openapi.json` desligados; `--no-server-header` |
| API10 Unsafe Consumption of APIs | A resposta do birô é validada; corpo inesperado devolve 502 |
