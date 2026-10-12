---
title: Como contribuir
summary: Clean Code aplicado às camadas, convenção de nomes, Conventional Commits, fluxo de branches, lint e checklist de PR.
related: [02-arquitetura/camadas.md, 07-testes/estrategia.md, 03-api/convencoes.md]
sources: [bootcamp-base-api (convenções), Aula 1 tarde, Aula 3 tarde (TDD), Dia 4 manhã nota 37]
---

# Como contribuir

> [Índice](README.md) › Contribuindo
>
> **Responde a:** como nomear? como comentar? como commitar? o que conferir antes do PR?

## Clean Code nas camadas

- **Uma responsabilidade por camada** ([camadas](02-arquitetura/camadas.md)):
  - `resources/` não tem regra nem `raise`. O teste `grep raise src/resources/` precisa voltar vazio.
  - `repositories/` não decide nada.
  - O `commit` fica só no controller, como última linha antes do `return`.
- **Funções pequenas e com nome de intenção.** Métodos privados do controller começam com `_` e dizem a regra: `_ensure_active`, `_check_bureau`, `_replay`. No repository, o nome diz o jeito de buscar: `lock_in_id_order`, `get_by_key_for_update`.
- **Erro é classe, não string.** Cada recusa nova vira uma classe em `src/errors/custom_errors.py` com o próximo código livre ([erros](03-api/erros.md)).
- **Sem números mágicos.** Tarifa, limite de contas e timeout vêm de `src/constants.py`, que lê o ambiente.
- **Comentário explica o porquê, nunca o quê**, em uma ou duas linhas. Raciocínio longo, medidas e trade-offs vão para o Markdown em `docs/`, e o código só aponta para ele.
- **Nada de código morto ou comentado.** O Git guarda o histórico.

## Nomes

| Item | Padrão | Exemplo |
|---|---|---|
| Arquivo | snake_case, singular | `transaction_controller.py` |
| Classe | `<Recurso><Camada>` | `TransactionController`, `AccountDTO`, `BureauConnector` |
| Método de resource | estilo Falcon do base-service | `on_post`, `on_get_by_key`, `on_get_list`, `on_put_status` |
| Schema | `<verbo>_<recurso>.json` | `post_transaction.json`, `get_transactions.json` |
| Tabela | snake_case, singular | `account_status_event` |
| Chave pública | `<entidade>_key` | `account_key` |
| Teste | `test_<ação>_<cenário>_returns_<status>` | `test_transfer_to_same_account_returns_422` |

Código, rotas e campos em inglês. Prosa da documentação e `translation` dos erros em português.

## Commits: Conventional Commits

```
<tipo>(<escopo opcional>): <resumo no imperativo, ≤ 72 caracteres>

<corpo opcional: o porquê da mudança>
```

- **Tipos:** `feat`, `fix`, `test`, `refactor`, `docs`, `chore`, `build`, `ci`.
- **Escopos:** `customer`, `account`, `transaction`, `bureau`, `infra`, `docs`.
- No TDD, o teste vermelho e a implementação podem ir no mesmo commit (`feat`) ou em commits separados (`test` e depois `feat`).
- Sem trailers de co-autoria ou de ferramenta.

Exemplos:

```
test(transaction): cover transfer without balance keeping both balances
feat(transaction): charge transfer fee in same database transaction
docs(rfc): describe lock ordering as main challenge
```

## Branches

- `main` sempre verde: sobe com `make up` e passa no `make test`.
- Branch por feature: `feat/<recurso>-<assunto>`, `fix/<assunto>` ou `docs/<assunto>`.
- Merge por PR com revisão de pelo menos uma pessoa do time.

## Lint

```bash
make lint        # ou: flake8 src tests
```

A configuração está em `.flake8` (linha de até 140 caracteres). O resultado precisa sair limpo.

## Checklist de PR

- [ ] Existe um teste que fica vermelho sem a mudança, e cada `if` novo tem os dois caminhos testados.
- [ ] Nenhum teste importa `src/` (R1).
- [ ] `make reset check` passa: banco do zero, lint limpo e testes verdes (R2).
- [ ] Erros novos estão no [catálogo](03-api/erros.md), com o próximo código livre atualizado.
- [ ] Rotas novas estão em [rotas.md](03-api/rotas.md). Decisões novas viraram ADR.
- [ ] As quatro perguntas foram respondidas: quem pode pedir, quanto tempo espero, o que acontece se pedirem duas vezes, como vou saber que falhou?
- [ ] Nenhum segredo no código. O `.env` não foi versionado.
