# .agents

Material para agentes de código, complementar ao [`AGENTS.md`](../AGENTS.md). A API e os testes não leem esta pasta.

```
.agents/
└── skills/                 receitas passo a passo, uma pasta por tarefa
    ├── nova-rota/          rota nova de ponta a ponta, com TDD
    ├── novo-erro/          recusa nova com código QIT
    ├── nova-decisao/       ADR novo
    └── revisar-mudanca/    checklist antes de abrir PR
```

Cada skill é um `SKILL.md` com front-matter `name` e `description` (formato [Agent Skills](https://agentskills.io)): a `description` diz quando usar, o corpo diz como. Skill nova: copie uma pasta, troque o front-matter e liste aqui. Ferramentas que procuram skills em outra pasta usam um link simbólico local ([docs/trabalhando-com-ia.md](../docs/trabalhando-com-ia.md)).
