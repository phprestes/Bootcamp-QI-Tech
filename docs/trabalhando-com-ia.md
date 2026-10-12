---
title: Trabalhando com IA
summary: Arquivos para agentes de código (AGENTS.md, .agents/, llms.txt) e regras de uso.
related: [contribuindo.md, ../AGENTS.md, ../llms.txt, 02-arquitetura/decisoes/0008-repositorio-ai-friendly.md]
sources: [agents.md, llmstxt.org, agentskills.io]
---

# Trabalhando com IA

> [Índice](README.md) › Trabalhando com IA
>
> **Responde a:** o que cada arquivo para agentes faz? como usar um agente aqui sem quebrar as regras?

O time trabalha com agentes de código, como é comum no mercado. Para o agente seguir as regras do projeto, elas precisam estar escritas num lugar que ele lê. A decisão está na [ADR 0008](02-arquitetura/decisoes/0008-repositorio-ai-friendly.md).

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| [`AGENTS.md`](../AGENTS.md) | Comandos, regras R1–R8, camadas, fluxo de trabalho e limites. Formato [agents.md](https://agents.md), lido pela maioria das ferramentas |
| [`.agents/skills/`](../.agents/README.md) | Passo a passo de tarefas recorrentes: nova rota, novo erro, nova decisão, revisar mudança |
| [`llms.txt`](../llms.txt) | Uma linha por documento. Formato [llmstxt.org](https://llmstxt.org) |
| `docs/**` | Front-matter e linha *Responde a* em todo documento |
| [`Makefile`](../Makefile) | Um comando por tarefa |

Os testes black box por HTTP são a rede de proteção: o agente pode refatorar, e se o contrato mudar o `pytest` acusa. Os ADRs registram o porquê das escolhas e evitam que o agente desfaça uma decisão deliberada.

## Uma fonte para todas as ferramentas

O `AGENTS.md` é a única fonte versionada. Ferramentas que leem outro arquivo apontam para ele:

| Ferramenta | Arquivo | Conteúdo |
|---|---|---|
| Codex, Cursor, Aider, Copilot (agente) | `AGENTS.md` | lê direto |
| Claude Code | `CLAUDE.md` | `@AGENTS.md` |
| Gemini CLI | `GEMINI.md` | `@AGENTS.md`, ou `contextFileName: "AGENTS.md"` no `settings.json` |
| Copilot (chat) | `.github/copilot-instructions.md` | link para o `AGENTS.md` |

Esses arquivos ficam fora do Git (`.git/info/exclude`). Preferência pessoal vai neles; regra do time vai no `AGENTS.md`. Para ferramentas que procuram skills em pasta própria:

```bash
mkdir -p .claude && ln -s ../.agents/skills .claude/skills
```

## Regras de uso

- Quem commita responde pelo código, escrito por agente ou não. Vale o mesmo [checklist de PR](contribuindo.md#checklist-de-pr).
- TDD vale para o agente: teste vermelho primeiro.
- Não cole `.env`, token real ou dado de cliente no agente.
- `make reset check` precisa passar antes de declarar pronto.
- Commit sem trailer de ferramenta.

## Manutenção

- Mudou regra, comando ou camada: atualize o `AGENTS.md` no mesmo PR.
- Tarefa que o agente erra com frequência vira skill em `.agents/skills/`.
- Documento novo entra no [índice](README.md) e no [`llms.txt`](../llms.txt).
