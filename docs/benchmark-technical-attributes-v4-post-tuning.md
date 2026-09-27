# Atributos técnicos v4 após tuning da v1.20

## Contexto

A baseline independente do v4 permanece registrada em:

`data/evaluation/technical-attributes-v4-baseline.json`

Resultado independente original:

- 45 exemplos;
- 42/45 categorias corretas;
- 87 campos técnicos avaliados;
- 77 campos técnicos corretos;
- micro accuracy de 88,51%;
- 9 falsos negativos;
- 1 falso positivo;
- nenhum mismatch.

## Correções aplicadas

A v1.20 corrige somente as lacunas observadas no v4:

- `ADESIVO FOTO` como evidência explícita de `light_cure`;
- `APINEFRINA` como `epinephrine`;
- `CONDICIONAMENTO ACIDO TOTAL` como `etch_and_rinse`;
- `RESINA FOTOPOLIMERIZAVEL` como resina composta quando usada como forma explícita de produto.

Também foi adicionada uma regra contextual para adesivos.

Quando a descrição contém `RESINA FOTOPOLIMERIZAVEL`, essa expressão não é usada automaticamente para inferir que o adesivo é fotopolimerizável. Isso evita o falso positivo observado no v4.

## Resultado pós-tuning

| Métrica | Resultado |
| --- | ---: |
| Exemplos | 45 |
| Categorias corretas | 45/45 |
| Acurácia de categoria | 100,00% |
| Campos técnicos avaliados | 87 |
| Campos técnicos corretos | 87 |
| Micro accuracy | 100,00% |
| Falsos positivos | 0 |
| Falsos negativos | 0 |
| Mismatches | 0 |

## Interpretação

Este resultado é regressão pós-tuning e não substitui a baseline independente.

As referências independentes continuam sendo:

- 93,33% de acurácia de categoria;
- 88,51% de micro accuracy técnica.

O principal ganho metodológico desta etapa foi introduzir uma regra de contexto negativo, não apenas ampliar o vocabulário.
