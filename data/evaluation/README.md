# Dataset de avaliação manual

Este diretório contém amostras pequenas e versionadas usadas para avaliar a taxonomia determinística.

## v1

O arquivo `v1.jsonl` contém descrições curtas de itens de compras públicas odontológicas publicadas em 2026.

Os registros preservam:

- ID interno estável;
- descrição curta usada no benchmark;
- categoria esperada;
- cor esperada quando aplicável;
- concentração esperada quando aplicável;
- número do item na fonte;
- número de controle PNCP quando disponível na página consultada;
- URL pública utilizada na rotulagem;
- estado do rótulo.

Os rótulos foram revisados manualmente a partir da descrição pública do item. Eles não devem ser tratados como padrão clínico universal nem como anotação infalível.

## Regras

1. Não ajustar um rótulo apenas para fazer o código passar.
2. Toda mudança de rótulo deve ter justificativa no histórico do Git.
3. Novas regras de taxonomia devem ser avaliadas contra a versão existente do dataset.
4. Exemplos difíceis e negativos devem permanecer na amostra.
5. Métricas do README só podem ser publicadas depois de execução real do benchmark.

## Execução

~~~bash
dpi evaluate-taxonomy --dataset data/evaluation/v1.jsonl
~~~

Para listar somente erros de categoria:

~~~bash
dpi evaluation-errors --dataset data/evaluation/v1.jsonl
~~~
