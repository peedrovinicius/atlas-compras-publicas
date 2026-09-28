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


## Atributos técnicos v6

O arquivo `technical-attributes-v6.jsonl` foi congelado depois do tuning do v5 e antes de qualquer nova correção.

A amostra contém:

- 48 descrições;
- 8 contratações inéditas;
- 90 campos técnicos revisados;
- 84 campos corretos na primeira medição;
- micro accuracy independente de 93,33%;
- 44/48 categorias corretas;
- 6 falsos negativos;
- nenhum falso positivo;
- nenhum mismatch.

A baseline está preservada em `technical-attributes-v6-baseline.json`.

~~~bash
dpi evaluate-technical-attributes \
  --dataset data/evaluation/technical-attributes-v6.jsonl
~~~


## Atributos técnicos v7

O arquivo `technical-attributes-v7.jsonl` foi congelado depois do tuning restrito da v1.24 e antes de qualquer nova correção.

A amostra contém:

- 48 descrições;
- 8 contratações inéditas;
- 83 campos técnicos revisados;
- 76 campos corretos na primeira medição;
- micro accuracy independente de 91,57%;
- 43/48 categorias corretas;
- 6 falsos negativos técnicos;
- 1 falso positivo técnico;
- nenhum mismatch.

A baseline está preservada em `technical-attributes-v7-baseline.json`.

~~~bash
dpi evaluate-technical-attributes \
  --dataset data/evaluation/technical-attributes-v7.jsonl
~~~

Os erros do v7 não são corrigidos na v1.25. Qualquer tuning posterior deve manter esta baseline imutável e registrar o novo resultado separadamente.


### Resultado pós-tuning v1.26

Após corrigir as lacunas observadas no v7, o mesmo conjunto congelado atingiu:

- 48/48 categorias corretas;
- 83/83 campos técnicos corretos;
- 100% de micro accuracy;
- nenhum falso positivo;
- nenhum falso negativo;
- nenhum mismatch.

O resultado está salvo em `technical-attributes-v7-post-v1.26.json`.

Esse valor é regressão pós-tuning e não substitui as baselines independentes de 89,58% para categoria e 91,57% para atributos.


## Atributos técnicos v8

O arquivo `technical-attributes-v8.jsonl` foi congelado após o tuning da v1.26 e antes da primeira medição válida.

A amostra contém:

- 48 descrições;
- 8 contratações inéditas;
- 83 campos técnicos revisados;
- 75 campos corretos na primeira medição;
- micro accuracy independente de 90,36%;
- 43/48 categorias corretas;
- 5 falsos positivos técnicos;
- 3 falsos negativos técnicos;
- nenhum mismatch.

A baseline está preservada em `technical-attributes-v8-baseline.json`.

As descrições usam trechos curtos e fiéis ao campo público do item, excluindo preço, quantidade e boilerplate de participação.

~~~bash
dpi evaluate-technical-attributes \
  --dataset data/evaluation/technical-attributes-v8.jsonl
~~~

Os erros do v8 não são corrigidos na v1.27. Qualquer tuning posterior deve manter esta baseline imutável e registrar o novo resultado separadamente.


### Resultado pós-tuning v1.28

Após corrigir as lacunas observadas no v8, o mesmo conjunto congelado atingiu:

- 48/48 categorias corretas;
- 83/83 campos técnicos corretos;
- 100% de micro accuracy;
- nenhum falso positivo;
- nenhum falso negativo;
- nenhum mismatch.

O resultado está salvo em `technical-attributes-v8-post-v1.28.json`.

Esse valor é regressão pós-tuning e não substitui as baselines independentes de 89,58% para categoria e 90,36% para atributos.


## Atributos técnicos v9

O arquivo `technical-attributes-v9.jsonl` foi congelado após o tuning da v1.28 e antes da primeira medição.

A amostra contém:

- 48 descrições;
- 8 contratações inéditas;
- 84 campos técnicos revisados;
- 81 campos corretos na primeira medição;
- micro accuracy independente de 96,43%;
- 42/48 categorias corretas;
- 1 falso positivo técnico;
- 2 falsos negativos técnicos;
- nenhum mismatch.

A baseline está preservada em `technical-attributes-v9-baseline.json`.

~~~bash
dpi evaluate-technical-attributes \
  --dataset data/evaluation/technical-attributes-v9.jsonl
~~~

Os erros do v9 não são corrigidos na v1.29. Qualquer tuning posterior deve manter esta baseline imutável e registrar o novo resultado separadamente.


### Resultado pós-tuning v1.30

Após corrigir as lacunas observadas no v9, o mesmo conjunto congelado atingiu:

- 48/48 categorias corretas;
- 84/84 campos técnicos corretos;
- 100% de micro accuracy;
- nenhum falso positivo;
- nenhum falso negativo;
- nenhum mismatch.

O resultado está salvo em `technical-attributes-v9-post-v1.30.json`.

Esse valor é regressão pós-tuning e não substitui as baselines independentes de 87,50% para categoria e 96,43% para atributos.


## Atributos técnicos v10

O arquivo `technical-attributes-v10.jsonl` foi congelado após o tuning da v1.30 e antes da primeira medição.

A amostra contém:

- 48 descrições;
- 8 contratações inéditas;
- 84 campos técnicos revisados;
- 80 campos corretos na primeira medição;
- micro accuracy independente de 95,24%;
- 45/48 categorias corretas;
- 1 falso positivo técnico;
- 3 falsos negativos técnicos;
- nenhum mismatch.

A baseline está preservada em `technical-attributes-v10-baseline.json`.

~~~bash
dpi evaluate-technical-attributes \
  --dataset data/evaluation/technical-attributes-v10.jsonl
~~~

Os erros do v10 não são corrigidos na v1.31. Qualquer tuning posterior deve manter esta baseline imutável e registrar o novo resultado separadamente.


### Resultado pós-tuning v1.32

Após corrigir as lacunas observadas no v10, o mesmo conjunto congelado atingiu:

- 48/48 categorias corretas;
- 84/84 campos técnicos corretos;
- 100% de micro accuracy;
- nenhum falso positivo;
- nenhum falso negativo;
- nenhum mismatch.

O resultado está salvo em `technical-attributes-v10-post-v1.32.json`.

Esse valor é regressão pós-tuning e não substitui as baselines independentes de 93,75% para categoria e 95,24% para atributos.


## Atributos técnicos v11

O arquivo `technical-attributes-v11.jsonl` foi congelado após o tuning da v1.32 e antes da primeira medição.

A amostra contém:

- 48 descrições;
- 8 contratações inéditas;
- 80 campos técnicos revisados;
- 74 campos corretos na primeira medição;
- micro accuracy independente de 92,50%;
- 36/48 categorias corretas;
- nenhum falso positivo técnico;
- 6 falsos negativos técnicos;
- nenhum mismatch.

A baseline está preservada em `technical-attributes-v11-baseline.json`.

~~~bash
dpi evaluate-technical-attributes \
  --dataset data/evaluation/technical-attributes-v11.jsonl
~~~

Os erros do v11 não são corrigidos na v1.33. Qualquer tuning posterior deve manter esta baseline imutável e registrar o novo resultado separadamente.


### Resultado pós-tuning v1.34

Após corrigir as lacunas observadas no v11, o mesmo conjunto congelado atingiu:

- 48/48 categorias corretas;
- 80/80 campos técnicos corretos;
- 100% de micro accuracy;
- nenhum falso positivo;
- nenhum falso negativo;
- nenhum mismatch.

O resultado está salvo em `technical-attributes-v11-post-v1.34.json`.

Esse valor é regressão pós-tuning e não substitui as baselines independentes de 75,00% para categoria e 92,50% para atributos.


## Atributos técnicos v12

- 48 descrições;
- 8 contratações inéditas;
- 77 campos técnicos revisados;
- 67 campos corretos na primeira medição;
- micro accuracy independente de 87,01%;
- 35/48 categorias corretas;
- 0 falsos positivos;
- 10 falsos negativos;
- 0 mismatches.

A baseline está preservada em `technical-attributes-v12-baseline.json`.

Os erros do v12 não são corrigidos na v1.35.


### Resultado pós-tuning v1.37

Após corrigir as lacunas observadas no v12, o mesmo conjunto congelado atingiu:

- 48/48 categorias corretas;
- 77/77 campos técnicos corretos;
- 100% de micro accuracy;
- nenhum falso positivo;
- nenhum falso negativo;
- nenhum mismatch.

O resultado está salvo em `technical-attributes-v12-post-v1.37.json`.

Esse valor é regressão pós-tuning e não substitui as baselines independentes de 72,92% para categoria e 87,01% para atributos.


## Medicamentos v1

- 48 exemplos;
- 8 contratações independentes;
- 192 campos avaliados;
- baseline independente de 87,50%;
- 168/192 campos corretos na primeira medição.

A baseline está preservada em `medications-v1-baseline.json`.

### Resultado pós-tuning v1.44

Após o tuning controlado:

- 48/48 exemplos;
- 192/192 campos corretos;
- 100% de micro accuracy;
- 0 falsos positivos;
- 0 falsos negativos;
- 0 mismatches.

O resultado está salvo em `medications-v1-post-v1.44.json`.

Esse resultado não substitui a baseline independente de 87,50%.


## Medicamentos v2

O arquivo `medications-v2.jsonl` foi congelado após o tuning da v1.44 e antes da primeira medição.

Resultado independente:

- 48 exemplos;
- 8 novas contratações;
- 192 campos avaliados;
- 153 campos corretos;
- micro accuracy de 79,69%;
- 0 falsos positivos;
- 0 falsos negativos;
- 39 mismatches.

Por campo:

- ingrediente ativo: 58,33%;
- concentração: 97,92%;
- forma farmacêutica: 81,25%;
- via: 81,25%.

A baseline está preservada em `medications-v2-baseline.json`.

Nenhuma lacuna do v2 é corrigida na v1.45.
