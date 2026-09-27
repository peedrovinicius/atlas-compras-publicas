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


## Atributos técnicos v3

O arquivo `technical-attributes-v3.jsonl` foi congelado depois do tuning do v2 e antes de qualquer nova correção.

A amostra contém:

- 45 descrições;
- 8 contratações inéditas;
- 86 campos técnicos revisados;
- 81 campos corretos na primeira medição;
- micro accuracy independente de 94,19%;
- 42/45 categorias corretas;
- 5 falsos negativos técnicos;
- nenhum falso positivo;
- nenhum mismatch.

A baseline está preservada em `technical-attributes-v3-baseline.json`.

~~~bash
dpi evaluate-technical-attributes \
  --dataset data/evaluation/technical-attributes-v3.jsonl
~~~


### Resultado pós-tuning v1.18

Após corrigir as lacunas observadas no v3, o mesmo conjunto congelado atingiu:

- 45/45 categorias corretas;
- 86/86 campos técnicos corretos;
- 100% de micro accuracy;
- nenhum falso positivo;
- nenhum falso negativo;
- nenhum mismatch.

O resultado está salvo em `technical-attributes-v3-post-v1.18.json`.

Esse valor é regressão pós-tuning e não substitui as baselines independentes de 93,33% para categoria e 94,19% para atributos.


## Atributos técnicos v4

O arquivo `technical-attributes-v4.jsonl` foi congelado depois do tuning do v3 e antes de qualquer nova correção.

A amostra contém:

- 45 descrições;
- 8 contratações inéditas;
- 87 campos técnicos revisados;
- 77 campos corretos na primeira medição;
- micro accuracy independente de 88,51%;
- 42/45 categorias corretas;
- 9 falsos negativos;
- 1 falso positivo contextual;
- nenhum mismatch.

A baseline está preservada em `technical-attributes-v4-baseline.json`.

~~~bash
dpi evaluate-technical-attributes \
  --dataset data/evaluation/technical-attributes-v4.jsonl
~~~


### Resultado pós-tuning v1.20

Após corrigir as lacunas técnicas e o falso positivo contextual observados no v4, o mesmo conjunto congelado atingiu:

- 45/45 categorias corretas;
- 87/87 campos técnicos corretos;
- 100% de micro accuracy;
- nenhum falso positivo;
- nenhum falso negativo;
- nenhum mismatch.

O resultado está salvo em `technical-attributes-v4-post-v1.20.json`.

Esse valor é regressão pós-tuning e não substitui as baselines independentes de 93,33% para categoria e 88,51% para atributos.


## Atributos técnicos v5

O arquivo `technical-attributes-v5.jsonl` foi congelado depois do tuning contextual da v1.20 e antes de qualquer nova correção.

A amostra contém:

- 48 descrições;
- 8 contratações inéditas;
- 92 campos técnicos revisados;
- 80 campos corretos na primeira medição;
- micro accuracy independente de 86,96%;
- 39/48 categorias corretas;
- 10 falsos negativos técnicos;
- 2 falsos positivos técnicos;
- nenhum mismatch.

A baseline está preservada em `technical-attributes-v5-baseline.json`.

~~~bash
dpi evaluate-technical-attributes \
  --dataset data/evaluation/technical-attributes-v5.jsonl
~~~


### Resultado pós-tuning v1.22

Após corrigir as lacunas de contexto, grafia e alternativas explícitas observadas no v5, o mesmo conjunto congelado atingiu:

- 48/48 categorias corretas;
- 92/92 campos técnicos corretos;
- 100% de micro accuracy;
- nenhum falso positivo;
- nenhum falso negativo;
- nenhum mismatch.

O resultado está salvo em `technical-attributes-v5-post-v1.22.json`.

Esse valor é regressão pós-tuning e não substitui as baselines independentes de 81,25% para categoria e 86,96% para atributos.
