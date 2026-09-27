# Refatoração declarativa do motor de regras v1.36

## Objetivo

Reduzir o acoplamento do motor de identidade sem alterar o comportamento observado.

## Mudanças estruturais

- criação de `identity/rules/models.py`;
- criação de `CategoryRuleSpec`;
- criação de `identity/rules/dental.py`;
- categorias odontológicas passam a ser declaradas com `rule_id`, prioridade e origem;
- o parser compila o registro declarativo preservando a mesma ordem;
- regras de atributos técnicos foram movidas para o módulo odontológico;
- o parser deixa de carregar diretamente a maior parte das tabelas de aliases.

## Guardrails

A refatoração não adiciona aliases do v12.

A validação protegida exige:

- IDs de regra únicos;
- prioridades únicas;
- precedência explícita preservada;
- termos não vazios;
- regressão técnica em 100% nos datasets v7, v8, v9, v10 e v11.

## Limitação operacional

O repositório ainda não possui GitHub Actions configurado. Os testes foram adicionados ao código e a equivalência foi auditada estruturalmente, mas não há execução automática de CI associada a esta release.

## Próximo passo

Somente após esta refatoração ser preservada no main o tuning do v12 pode adicionar novos aliases e contextos.
