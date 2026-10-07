---
title: Observabilidade
summary: Logs estruturados com request id, erros nomeados, health check, métricas (p95, taxa de 5xx) e alarmes.
related: [seguranca.md, resiliencia.md, ../03-api/erros.md]
sources: [Dia 4 manhã notas 6-17 e 34, One-page Dia 4, Autoestudo Aula 4 #1-3]
---

# Observabilidade

> [Índice](../README.md) › Operação › Observabilidade
>
> **Responde a:** como descubro o que aconteceu com um pedido? como sei que o sistema está saudável? quem é avisado?

Princípio da aula: entender o que aconteceu **pelos sinais que o sistema emitiu**, sem entrar na máquina. O container é efêmero e a réplica das 3h da manhã já morreu.

## Os três sinais

| Sinal | Responde | No projeto |
|---|---|---|
| **Log** | O que aconteceu com *este* pedido? | ✅ Middleware `request_logger` com ENTROU/SAIU e logs de negócio no controller |
| **Métrica** | Como está o sistema *agora*? | Infraestrutura (fora do base-service); proposta abaixo |
| **Trace** | Onde o tempo foi gasto entre serviços? | Infraestrutura; com um serviço só, o log com tempo basta |

## Logs

- Formato: `%(asctime)s [%(levelname)s] %(name)s [%(request_id)s] - %(message)s`.
- O **`X-Request-ID`** costura log, resposta e erro. Ele é gerado no middleware `request_context`, ou reaproveitado se vier válido no pedido, e volta no header da resposta.
- O log vem **antes** do token na cadeia de middlewares, então até a tentativa barrada com 403 fica registrada.
- No controller, use `logger.info` nas decisões (ex.: "transferência recusada: saldo insuficiente") e `logger.debug` nos detalhes.
- **Nunca logar** CPF completo, token ou corpo inteiro. Mascare (`***.***.***-09`).
- O connector loga `OUTGOING`/`INCOMING` com status e duração.

## Erros como sinal

Cada recusa prevista é uma classe com código próprio ([erros](../03-api/erros.md)). Um `500 QIT000500` significa **um erro que ninguém nomeou ainda**: ele gera `logger.exception` e vira tarefa de nomear.

## Health check

`GET /health_check` responde `204` **sem tocar o banco**, para não derrubar a réplica quando o banco oscila. Ele é usado:

- pelo compose, a cada 3s;
- em produção, pelo load balancer, para decidir para quem mandar tráfego.

## Métricas e alarmes (proposta para produção)

| Métrica | Fonte | Alarme |
|---|---|---|
| Latência p95 | tráfego | p95 > 500 ms por 5 min → time dono |
| Taxa de 5xx | tráfego | > 1% por 5 min |
| Taxa de 502 (birô) | tráfego | > 5% por 5 min → indica birô degradado |
| CPU | orquestrador | CPU alta é **sempre** emergência |
| Memória | orquestrador | crescimento contínuo indica vazamento |

Um alarme é **sinal + limite + prazo + dono**, e todo alarme pede uma ação. Na QI, os alertas vão para o OpsGenie (P1–P5). Os números acima são ilustrativos.
