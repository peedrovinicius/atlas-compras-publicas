# Revisão do README para v1.49.0

## Objetivo

Registrar a revisão editorial do README após o fechamento do ciclo de medicamentos v4 e da release v1.49.0.

## Resultado da revisão

O README já estava alinhado com o v4 antes desta release:

- inclui medicamentos v1–v4;
- mostra 192 exemplos e 768 campos de medicamentos;
- aponta para `docs/benchmark-medications-v4.md`;
- aponta para `docs/benchmark-medications-consolidated-v1-v4.md`;
- preserva a distinção entre baseline independente e pós-tuning;
- mantém o domínio em `benchmark_required`.

## Decisão editorial

Não foi necessário inflar o README com todos os detalhes do pós-tuning v1.49.0.

A decisão foi manter o README como vitrine técnica objetiva e deixar os detalhes completos nos documentos especializados:

- `docs/benchmark-medications-v4-post-tuning.md`;
- `docs/benchmark-medications-consolidated-v1-v4.md`;
- `docs/release-v1.49.0.md`.

## Critérios conferidos

- Sem linguagem promocional excessiva.
- Sem simular painel de preço ou homologação ainda não consolidado.
- Sem substituir baseline independente por pós-tuning.
- Sem evidenciar uso de IA.
- Sem excesso de detalhe operacional no README principal.

## Próxima revisão sugerida

Revisar o README novamente quando houver base DuckDB real consolidada para painel de preços, homologações e sinais estatísticos.
