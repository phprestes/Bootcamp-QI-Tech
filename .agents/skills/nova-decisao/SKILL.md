---
name: nova-decisao
description: Use ao tomar uma decisão de arquitetura ou de processo que alguém vai questionar depois. Registra um ADR com alternativas e preço.
---

# Nova decisão (ADR)

1. Copie um ADR de [docs/02-arquitetura/decisoes/](../../../docs/02-arquitetura/decisoes/README.md) com o próximo número (`NNNN-titulo-curto.md`).
2. Preencha o front-matter (`title`, `summary`, `related`, `sources`) e mantenha as seções: Contexto → Decisão → Alternativas descartadas (cada uma com Preço e Ganharia se) → Consequências. Escreva no presente.
3. Adicione a linha na tabela do índice de decisões e no [`llms.txt`](../../../llms.txt).
4. Se a decisão aparece na RFC, atualize [docs/rfc/RFC.md](../../../docs/rfc/RFC.md) a partir do ADR, nunca o contrário.
