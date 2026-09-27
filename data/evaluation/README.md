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


## Atributos técnicos

O arquivo `technical-attributes-v1.jsonl` avalia a extração de atributos técnicos separadamente da taxonomia principal.

A amostra contém 33 descrições e 61 campos revisados manualmente. A baseline independente original está preservada em `technical-attributes-v1-baseline.json`.

Execução:

~~~bash
dpi evaluate-technical-attributes \
  --dataset data/evaluation/technical-attributes-v1.jsonl
~~~

Para listar divergências:

~~~bash
dpi technical-attribute-errors \
  --dataset data/evaluation/technical-attributes-v1.jsonl
~~~

A baseline publicada não deve ser sobrescrita por resultados pós-tuning.


## Atributos técnicos v2

O arquivo `technical-attributes-v2.jsonl` é um novo benchmark independente, congelado após o tuning do v1 e antes de qualquer nova correção.

A amostra contém:

- 41 descrições;
- 8 contratações inéditas;
- 77 campos técnicos revisados;
- 72 campos corretos na primeira medição;
- micro accuracy independente de 93,51%;
- 5 falsos negativos;
- nenhum falso positivo;
- nenhum mismatch.

A baseline está preservada em `technical-attributes-v2-baseline.json`.

~~~bash
dpi evaluate-technical-attributes \
  --dataset data/evaluation/technical-attributes-v2.jsonl
~~~


### Resultado pós-tuning v1.16

Após corrigir as cinco lacunas observadas no v2, o mesmo conjunto congelado atingiu 77/77 campos corretos.

O resultado está salvo em `technical-attributes-v2-post-v1.16.json`.

Esse valor é regressão pós-tuning e não substitui a baseline independente de 93,51%.
