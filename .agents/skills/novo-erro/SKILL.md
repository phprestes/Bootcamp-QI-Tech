---
name: novo-erro
description: Use quando uma regra precisa recusar um pedido com um código QIT novo. Cobre a classe de erro, o catálogo e o teste.
---

# Novo erro

1. Abra [docs/03-api/erros.md](../../../docs/03-api/erros.md) e pegue o próximo código livre da faixa `QIT002xxx`.
2. Escreva o teste que espera `status` e `response["code"]` com esse código.
3. Crie a classe em `src/errors/custom_errors.py`, copiando o formato das vizinhas: `code` como atributo de classe, `title` e `description` em inglês, `translation` em português (R3).
4. Status: 404 para recurso inexistente ou de outro dono (R8, nunca 403); 409 para conflito de estado; 422 para regra de negócio; 502 para falha do birô.
5. Levante o erro no controller (nunca no resource).
6. Adicione a linha no catálogo e atualize o próximo código livre. Se a rota mudou, atualize também [rotas.md](../../../docs/03-api/rotas.md).
7. `make reset check`. Código duplicado derruba o boot.
