# Atributos técnicos v10 após tuning da v1.32

## Contexto

A baseline independente do v10 permanece registrada em:

`data/evaluation/technical-attributes-v10-baseline.json`

Resultado independente original:

- 48 exemplos;
- 45/48 categorias corretas;
- 84 campos técnicos avaliados;
- 80 campos técnicos corretos;
- micro accuracy de 95,24%;
- 1 falso positivo;
- 3 falsos negativos;
- nenhum mismatch.

## Correções aplicadas

A v1.32 trata apenas as lacunas observadas no v10:

- `FLUOR TÓPICO GEL` passa a participar da identidade de gel fluoretado;
- `FOTOATIVAO` e `CURA PELA LUZ` passam a representar cura por luz;
- ionômero de vidro explicitamente reforçado por resina continua classificado como ionômero;
- cimento com óxido de zinco não é reduzido à categoria da substância apenas porque a composição a menciona;
- cimento com eugenol permanece fora da categoria isolada de eugenol;
- vasoconstritor passa a ser extraído somente quando há um único valor canônico; sinônimos da mesma substância continuam válidos, enquanto norepinefrina + epinefrina ficam indeterminadas.

## Limites preservados

As regras continuam contextuais:

- solução bucal de fluoreto de sódio não vira gel fluoretado;
- resina composta comum continua classificada como resina;
- óxido de zinco isolado continua `zinc_oxide`;
- eugenol isolado continua `eugenol`;
- epinefrina + adrenalina continuam equivalentes e produzem `epinephrine`;
- selantes que citam resina continuam fora da categoria de resina quando aplicável.

## Validação de regressão

O espelho determinístico do parser atualizado foi executado sobre três datasets congelados:

| Dataset | Categorias | Atributos |
| --- | ---: | ---: |
| v8 pós-tuning | 48/48 | 83/83 |
| v9 pós-tuning | 48/48 | 84/84 |
| v10 pós-tuning | 48/48 | 84/84 |

As novas regras atingem os cinco registros únicos que concentravam todas as divergências do v10:

- `ta10-cmi-042`;
- `ta10-cmi-043`;
- `ta10-sum-115`;
- `ta10-min-329`;
- `ta10-fbe-180`.

## Resultado pós-tuning

| Métrica | Resultado |
| --- | ---: |
| Exemplos | 48 |
| Categorias corretas | 48/48 |
| Acurácia de categoria | 100,00% |
| Campos técnicos avaliados | 84 |
| Campos técnicos corretos | 84 |
| Micro accuracy | 100,00% |
| Falsos positivos | 0 |
| Falsos negativos | 0 |
| Mismatches | 0 |

## Interpretação

Este resultado é regressão pós-tuning e não substitui a baseline independente.

As referências independentes continuam sendo:

- 93,75% de acurácia de categoria;
- 95,24% de micro accuracy técnica.

O próximo benchmark técnico deve usar novas contratações e ser congelado antes de qualquer ajuste adicional.
