---
title: "ADR 0008: Repositório AI-friendly"
summary: AGENTS.md como fonte única de instruções para agentes, receitas em .agents/skills/ e llms.txt; arquivos específicos de cada ferramenta ficam locais e só apontam para o AGENTS.md.
related: [../../trabalhando-com-ia.md, ../../contribuindo.md]
sources: [agents.md, llmstxt.org, agentskills.io]
---

# ADR 0008: Repositório AI-friendly

> [Índice](../../README.md) › [Decisões](README.md) › 0008

**Status:** aceita

## Contexto

O time usa agentes de código, cada pessoa com uma ferramenta. Sem instrução escrita, o agente importa `src/` no teste, põe regra no resource e inventa código de erro. As regras existiam em `docs/`, mas espalhadas.

## Decisão

- **`AGENTS.md` na raiz** é a fonte única de instruções para agentes: comandos, regras R1–R8, camadas, fluxo e limites. Formato aberto [agents.md](https://agents.md).
- **`.agents/skills/<tarefa>/SKILL.md`** guarda receitas de tarefas recorrentes, neutras de ferramenta.
- **`llms.txt`** continua como mapa da documentação para LLMs.
- Arquivos de ferramenta (`CLAUDE.md`, `GEMINI.md`, `.claude/`, `.cursor/`) ficam fora do Git e só apontam para o `AGENTS.md`.

## Alternativas descartadas

- **Um arquivo por ferramenta, versionado (`CLAUDE.md`, `.cursorrules`, `GEMINI.md`…).**
  - **Preço:** o mesmo conteúdo em vários lugares, que divergem no primeiro PR esquecido.
  - **Ganharia se** o time inteiro usasse uma única ferramenta e quisesse recursos exclusivos dela.
- **Nada específico; o agente lê `docs/`.**
  - **Preço:** o agente gasta contexto lendo tudo e ainda erra regra escondida; a pessoa repete a instrução em todo pedido.
  - **Ganharia se** o projeto fosse pequeno a ponto de caber inteiro no contexto.

## Consequências

O `AGENTS.md` muda no mesmo PR que mudar regra, comando ou camada. Ele resume e aponta para `docs/`; em divergência, vale o documento de origem. Uso em [trabalhando-com-ia.md](../../trabalhando-com-ia.md).
