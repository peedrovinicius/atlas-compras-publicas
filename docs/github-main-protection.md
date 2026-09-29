# Proteção da branch main

Este documento registra a configuração recomendada para a branch `main` do Atlas.

## Objetivo

A `main` representa código pronto para produção. Mudanças devem chegar por Pull Request depois da validação na `develop`.

## Configuração recomendada

No GitHub, abra:

`Settings → Rules → Rulesets`

Crie um ruleset para branches com alvo:

`main`

Configure:

- exigir Pull Request antes do merge;
- exigir que os checks de status passem;
- exigir o check `quality`;
- bloquear force push;
- bloquear exclusão da branch;
- impedir bypass por padrão;
- manter a regra ativa.

Para este repositório, não é necessário exigir múltiplas aprovações enquanto houver apenas um mantenedor. O objetivo principal é impedir merge acidental sem CI e proteger a branch contra reescrita ou exclusão.

## Fluxo esperado

```text
develop
  ↓
CI: quality
  ↓
Pull Request
  ↓
main
  ↓
Render
```

## Validação

Depois de salvar a regra:

1. abra a página da branch `main`;
2. confirme que ela aparece como protegida;
3. confirme que force push está bloqueado;
4. confirme que exclusão está bloqueada;
5. confirme que um PR para `main` exige o check `quality`;
6. registre a conclusão na issue #28.

## Exceções administrativas

Evite bypass administrativo para mudanças comuns.

Se uma exceção for necessária por incidente de produção, registre o motivo na issue ou no Pull Request correspondente.

## Relação com deploy

A proteção da `main` não substitui o gate do Render.

O fluxo completo esperado é:

1. trabalho na `develop`;
2. CI aprovada;
3. PR para `main`;
4. merge;
5. Render publica somente a mudança consolidada;
6. workflow manual `Production smoke test` valida produção.
