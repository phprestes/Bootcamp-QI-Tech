---
title: Como gerar e revisar a RFC
summary: Exportar RFC.md para PDF (entrega) e checklist do modelo da Aula 2 antes de enviar.
related: [RFC.md, ../README.md]
sources: [bootcamp-rfc-modelo.md, Aula 2 p.66-73 (defeitos de RFC), Aula 4 tarde (PDF com lógica de RFC)]
---

# Como gerar e revisar a RFC

> [Índice](../README.md) › RFC › Como gerar
>
> **Responde a:** como transformar a RFC em PDF? o que conferir antes de entregar?

## Exportar para PDF

O PDF é entregue com o repositório até 12/10, às 12h.

Com o pandoc mais o filtro de Mermaid:

```bash
npx -y @mermaid-js/mermaid-cli -i docs/rfc/RFC.md -o /tmp/rfc-rendered.md   # renderiza os blocos mermaid em SVG
pandoc /tmp/rfc-rendered.md -o RFC.pdf --pdf-engine=wkhtmltopdf
```

Sem ferramentas: abra `RFC.md` no GitHub, que renderiza Mermaid, e use Imprimir → Salvar como PDF.

O PDF não é versionado. Ele é anexado na entrega.

## Checklist do modelo

- [ ] Time, data e versão preenchidos. O bloco "Como usar este modelo" foi removido.
- [ ] O corpo (Contextualização e Implementação) segue as seções do modelo. O detalhe que passa do alvo de 2 a 4 páginas fica nos anexos, para a RFC se explicar sem o repositório.
- [ ] "Entendendo o problema" não fala de rota, tabela nem biblioteca.
- [ ] "Solução macro": um parágrafo mais 2 a 4 alternativas descartadas, cada uma com o preço e o cenário em que ganharia (R7).
- [ ] Rotas com status explícitos (400, 404, 409, 422, 502) e a idempotência dita.
- [ ] Banco de dados só com diagrama; invariantes e índices vão no Anexo E.
- [ ] Cada operação principal tem caminho feliz e pelo menos uma falha, dizendo o que é travado e o que é desfeito.
- [ ] Um único bloco "Principal desafio", na seção onde o desafio mora.
- [ ] O texto está no presente da proposta, não no passado ("foi decidido").
- [ ] Há números, caminhos de arquivo e nomes de teste. Uma afirmação sem prova é um defeito.
- [ ] O ecossistema mostra cada serviço do compose.
- [ ] Toda regra da RFC tem um teste, conferido na [matriz regra → teste](../01-contexto/requisitos.md#matriz-regra--teste).
