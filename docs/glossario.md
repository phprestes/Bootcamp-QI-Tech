---
title: Glossário
summary: Definição curta de cada termo usado na documentação e nas aulas.
related: [README.md, 03-api/convencoes.md, 04-dados/modelo.md]
sources: [One-page Dia 2, Guia Dia 3, One-page Dia 4]
---

# Glossário

> [Índice](README.md) › Glossário
>
> **Responde a:** o que significa este termo no projeto?

| Termo | Definição no projeto |
|---|---|
| **ACID** | As quatro garantias de uma transação de banco: Atomicidade (tudo ou nada), Consistência (as constraints valem), Isolamento (uma transação não vê o rascunho da outra) e Durabilidade (o commit é permanente). |
| **Alarme** | Sinal + limite + prazo + dono. Todo alarme pede uma ação. |
| **Append-only** | Uma mudança vira uma linha nova e nada é apagado nem editado. Soft delete não conta como append-only (R4). |
| **API Gateway** | A única porta pública. Confere quem vem de fora; o `INTERNAL-TOKEN` nunca sai da rede interna. |
| **Birô (bureau)** | Serviço externo que informa a situação do CPF. Nos testes, quem responde é o Mockserver. |
| **Black box (teste)** | Teste que fala com a API só por HTTP e confere status e corpo. Não importa nada de `src/` (R1). |
| **Connector** | Camada que fala com serviços de fora. Guarda endereço, timeout e o desembrulho da resposta, mas não decide nada. |
| **Controller** | Onde mora a regra de negócio e a ordem dos passos. É o único lugar que dá `commit`. |
| **DTO** | Converte o objeto do banco no JSON de saída e escolhe o que sai e com que nome. |
| **Enumerador (status)** | Tabela com a lista fixa de estados que uma entidade pode ter. |
| **Evento (tabela de)** | Uma linha por mudança de estado, para saber desde quando e por quê. |
| **Extrato** | Lista paginada das transações de uma conta, da qual o saldo pode ser reconstruído. |
| **Health check** | `GET /health_check`, que só responde "estou de pé". Não toca o banco. |
| **id × key** | `id` é o número sequencial interno, que nunca sai da API. `<entidade>_key` é o UUID público que aparece na URL e nas respostas (R5). |
| **Idempotência** | Repetir o mesmo pedido não executa a operação duas vezes. Aqui é garantida pela `request_control_key` com `UNIQUE` no banco. |
| **IDOR** | Insecure Direct Object Reference: acessar o recurso de outra pessoa trocando o identificador. Aqui a resposta é 404, nunca 403 (R8). |
| **INTERNAL-TOKEN** | Cabeçalho que toda requisição precisa trazer (exceto `/` e `/health_check`). Se faltar ou não bater, a resposta é 403. |
| **Lock pessimista** | `SELECT … FOR UPDATE` (`with_for_update()`): trava a linha até o commit. |
| **Middleware** | Camada por fora da aplicação que vale para toda requisição: request id, log, token e sessão. |
| **Mockserver** | Servidor HTTP falso que roda num container e finge ser o serviço de fora. Recebe *expectation* (o roteiro) e *verify* (confere a chamada). |
| **QIT code** | Código único de cada erro (`QIT000001`…), presente no corpo de toda recusa (R3). |
| **Repository** | A única camada que fala com o banco. Busca e guarda, mas não decide. |
| **Request id** | `X-Request-ID`, que costura todas as linhas de log de um mesmo pedido. |
| **`request_control_key`** | Chave de idempotência (UUID) gerada por quem chama, no padrão da QI Tech. |
| **RFC** | Documento que propõe e defende um desenho antes do código, junto com as alternativas descartadas (R7). |
| **Schema** | Arquivo JSON Schema que confere o formato da entrada antes de qualquer regra rodar. |
| **Tarifa (fee)** | Valor cobrado da conta de origem em cada transferência, gravado como uma transação `FEE`. |
| **Timeout** | Tempo máximo que a API espera por um serviço de fora. Fica escrito no connector. |
