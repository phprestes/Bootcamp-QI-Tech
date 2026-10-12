---
title: Índice da documentação
summary: Mapa de todos os documentos do projeto, cada um com a pergunta que responde. Comece por aqui.
related: [../README.md, ../llms.txt, rfc/RFC.md]
sources: [Bootcamp QI Tech 2026, Aulas 1 a 4]
---

# Documentação — Banco digital (Bootcamp QI Tech 2026)

> **Repositório AI-friendly:** agentes de código começam pelo [`AGENTS.md`](../AGENTS.md); o porquê está em [trabalhando com IA](trabalhando-com-ia.md).
>
> **Como navegar:** cada documento trata de um assunto só, abre com front-matter (`title`, `summary`, `related`, `sources`) e com a linha *Responde a*. Os links são relativos e os diagramas são Mermaid (texto). A [RFC](rfc/RFC.md) é derivada destes documentos: quando eles divergirem, quem manda é o documento de origem.

## Leitura mínima (10 minutos)

1. [Problema](01-contexto/problema.md): o que o sistema faz e que garantias dá sobre o dinheiro.
2. [Visão geral](02-arquitetura/visao-geral.md): as peças e como se encaixam.
3. [Rotas](03-api/rotas.md): o contrato.
4. [Transferência](05-fluxos/transferencia.md): o principal desafio.

## Mapa completo

| Documento | Responde a |
|---|---|
| [glossario.md](glossario.md) | O que significa cada termo (key, ACID, idempotência, IDOR…)? |
| **01 · Contexto** | |
| [problema.md](01-contexto/problema.md) | O que o sistema faz, para quem, e o que está fora do escopo? |
| [requisitos.md](01-contexto/requisitos.md) | Quais restrições (R1–R8) e regras de negócio valem, e qual teste prova cada uma? |
| **02 · Arquitetura** | |
| [visao-geral.md](02-arquitetura/visao-geral.md) | Quais serviços sobem, quem chama quem? |
| [camadas.md](02-arquitetura/camadas.md) | Em qual pasta mora cada coisa e o que ela não pode fazer? |
| [decisoes/](02-arquitetura/decisoes/README.md) | Por que cada escolha foi feita, e o que foi descartado? |
| **03 · API** | |
| [convencoes.md](03-api/convencoes.md) | Como nomear rotas, que status devolver, como paginar e autenticar? |
| [rotas.md](03-api/rotas.md) | Quais rotas existem, com entrada, saídas e idempotência? |
| [erros.md](03-api/erros.md) | Qual código QIT sai em cada recusa? |
| **04 · Dados** | |
| [modelo.md](04-dados/modelo.md) | Quais tabelas, chaves e constraints existem? |
| [estados.md](04-dados/estados.md) | Quais estados a conta tem e quais transições valem? |
| **05 · Fluxos** | |
| [criar-cliente.md](05-fluxos/criar-cliente.md) | Passo a passo do cadastro de cliente, incluindo a consulta ao birô |
| [abrir-conta.md](05-fluxos/abrir-conta.md) | Passo a passo da abertura de conta |
| [deposito.md](05-fluxos/deposito.md) | Passo a passo do depósito |
| [transferencia.md](05-fluxos/transferencia.md) | Transferência com tarifa, travas e idempotência (principal desafio) |
| [extrato.md](05-fluxos/extrato.md) | Extrato paginado e como ele reconstrói o saldo |
| **06 · Operação** | |
| [rodando-localmente.md](06-operacao/rodando-localmente.md) | Como subir, testar e resetar; armadilhas comuns |
| [observabilidade.md](06-operacao/observabilidade.md) | Como saber o que aconteceu (logs, request id, métricas, alarmes)? |
| [seguranca.md](06-operacao/seguranca.md) | Quem pode chamar, como os segredos são guardados, IDOR |
| [resiliencia.md](06-operacao/resiliencia.md) | Timeout, 502, retry e pedido repetido |
| **07 · Testes** | |
| [estrategia.md](07-testes/estrategia.md) | Como testamos (black box, TDD, Mockserver) e como rodar |
| **Processo** | |
| [contribuindo.md](contribuindo.md) | Clean Code, commits, branches, lint, checklist de PR |
| [trabalhando-com-ia.md](trabalhando-com-ia.md) | Por que o repositório é AI-friendly e como usar agentes (`AGENTS.md`, `.agents/`, `llms.txt`)? |
| [rfc/RFC.md](rfc/RFC.md) | O documento de entrega (vira PDF). Autossuficiente: corpo no modelo da aula e anexos com todo o detalhe |
| [rfc/README.md](rfc/README.md) | Como exportar a RFC e o checklist do modelo |
| [referencia/base-service-readme.md](referencia/base-service-readme.md) | README original do serviço-base (exemplo `sample_entity`) |

## Datas

| Data | Marco |
|---|---|
| **12/10, até 12h** | Entrega da fase 1: repositório público no GitHub + PDF da RFC. A banca avalia o repositório como estiver nesse momento. |
| 12 a 15/10 | A banca avalia as entregas |
| 16/10 | Divulgação dos finalistas |
| 17 e 18/10 | Fase final presencial, com um novo desafio que complementa o primeiro |
