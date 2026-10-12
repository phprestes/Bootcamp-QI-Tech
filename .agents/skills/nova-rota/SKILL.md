---
name: nova-rota
description: Use ao criar ou mudar uma rota HTTP da API (POST, GET, PUT). Guia o ciclo TDD pelas camadas e a atualização da documentação.
---

# Nova rota

1. **Contrato primeiro.** Siga a [ADR 0007](../../../docs/02-arquitetura/decisoes/0007-convencao-de-rotas.md): item no singular, lista no plural, aninhamento só onde há posse. Escreva a linha da rota em [docs/03-api/rotas.md](../../../docs/03-api/rotas.md) com entradas, saídas (status e código QIT) e idempotência.
2. **Teste vermelho.** Em `tests/integration/<recurso>/`, um teste por saída da tabela, nomeado `test_<ação>_<cenário>_returns_<status>`, com docstring citando a regra. Prepare o cenário pela API com `ObjectGenerator`/`RequestGenerator` de `tests/utils/`; nunca importe `src/` nem leia o banco (R1). Rode `make test` e confirme que falha pelo motivo certo.
3. **Implemente de fora para dentro**, respeitando [camadas.md](../../../docs/02-arquitetura/camadas.md):
   - `src/schemas/<verbo>_<recurso>.json` com `additionalProperties: false`.
   - `src/resources/<recurso>.py`: método `on_<verbo>…`, sem regra e sem `raise`.
   - `src/controllers/<recurso>_controller.py`: regra e o único `session.commit()`.
   - `src/repositories/`: só consulta; `with_for_update()` se lê-decide-escreve.
   - `src/dtos/`: só `<entidade>_key`, nunca `id` (R5).
   - Registre em `src/app.py` com `add_api_route`.
4. **Recusa nova?** Siga a skill [novo-erro](../novo-erro/SKILL.md).
5. **Verde e limpo:** `make reset check`.
