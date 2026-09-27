# Atributos técnicos v5 após tuning da v1.22

## Contexto

A baseline independente do v5 permanece registrada em:

`data/evaluation/technical-attributes-v5-baseline.json`

Resultado independente original:

- 48 exemplos;
- 39/48 categorias corretas;
- 92 campos técnicos avaliados;
- 80 campos técnicos corretos;
- micro accuracy de 86,96%;
- 10 falsos negativos;
- 2 falsos positivos;
- nenhum mismatch.

## Correções aplicadas

A v1.22 trata somente as lacunas observadas no v5:

- produto principal preservado quando a descrição apenas menciona adesivo;
- `APLICADOR DE ADESIVO` excluído da categoria de adesivo;
- selante que apenas contém resina não é tratado como resina composta;
- alternativas explícitas como `MICRO-HIBRIDA OU NANO-HIBRIDA` não recebem uma tecnologia única;
- `FOTOPOLIMERIZALVEL` e `FOTOPOLIMERIXAVE` tratados como `light_cure`;
- `MICROHIDRIDA` tratada como `microhybrid`;
- `RESINA ODONTOLOGICA`, `RESINA FORMA NANOHIBRIDA`, `RESINA FOTO`, `FLUOR NEUTRO` e `FLUOR ACIDULADO` reconhecidos quando usados como formas explícitas de produto.

## Resultado pós-tuning

| Métrica | Resultado |
| --- | ---: |
| Exemplos | 48 |
| Categorias corretas | 48/48 |
| Acurácia de categoria | 100,00% |
| Campos técnicos avaliados | 92 |
| Campos técnicos corretos | 92 |
| Micro accuracy | 100,00% |
| Falsos positivos | 0 |
| Falsos negativos | 0 |
| Mismatches | 0 |

## Interpretação

Este resultado é regressão pós-tuning e não substitui a baseline independente.

As referências independentes continuam sendo:

- 81,25% de acurácia de categoria;
- 86,96% de micro accuracy técnica.

O principal ganho metodológico desta etapa foi tratar produto principal, contexto negativo e alternativas explícitas em vez de apenas ampliar o vocabulário.
