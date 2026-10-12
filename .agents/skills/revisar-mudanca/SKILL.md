---
name: revisar-mudanca
description: Use antes de declarar uma tarefa pronta ou abrir PR. Checklist das regras avaliadas, com o comando que verifica cada uma.
---

# Revisar mudança

Rode e leia a saída; não declare pronto sem ela.

```bash
make reset check                        # R2 + lint + testes, banco do zero
grep -rn "from src\|import src" tests/  # R1: precisa voltar vazio
grep -rn "raise" src/resources/         # resource sem raise: precisa voltar vazio
grep -rn "float" src/                   # R6: dinheiro nunca em float
```

Depois confira à mão:

- [ ] Cada `if` novo tem um teste que passa e um recusado.
- [ ] Nenhum DTO devolve `id` ou FK (R5).
- [ ] Recurso de outro dono devolve 404 (R8).
- [ ] `session.commit()` só no controller, como última linha antes do `return`.
- [ ] Rota, erro ou decisão nova estão em `rotas.md`, `erros.md` ou num ADR.
- [ ] Nenhum segredo no diff; `.env` fora do Git.
- [ ] Commit em Conventional Commits, sem trailer de ferramenta.

Checklist completo de PR: [docs/contribuindo.md](../../../docs/contribuindo.md#checklist-de-pr).
