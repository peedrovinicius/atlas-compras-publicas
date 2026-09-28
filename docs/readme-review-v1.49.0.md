# Revisão do README v1.49.0

## Objetivo

Registrar a revisão editorial do README após o fechamento da release v1.49.0 e o início da auditoria.

## Decisão editorial

O README deve funcionar como vitrine técnica do projeto, não como histórico completo de implementação.

Por isso, a versão revisada:

- apresenta o propósito do Atlas com linguagem direta;
- mantém arquitetura, stack, validação, medicamentos, snapshot e uso rápido;
- resume medicamentos v1-v4 sem transformar o README em relatório completo;
- separa baseline independente e pós-tuning v1.49;
- aponta os detalhes para documentos técnicos;
- evita excesso de explicação operacional;
- usa `->` na cadeia de rastreabilidade em vez de travessão.

## Correções feitas

- Removido texto desatualizado que dizia que o v4 não possuía pós-tuning.
- Incluído o resultado pós-tuning v1.49, 192/192.
- Incluído link para `docs/benchmark-medications-v4-post-tuning.md`.
- Mantida a baseline independente v4 como referência metodológica principal.
- Mantido o domínio em `benchmark_required`.
- Reduzida a lista de documentos no README para os links essenciais.

## Estado recomendado

A versão atual está adequada para apresentação pública técnica.

Próximas melhorias devem ser pontuais e visuais, não aumento de texto.
