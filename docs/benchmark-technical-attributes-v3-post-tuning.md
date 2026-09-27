# Atributos técnicos v3 após tuning da v1.18

## Contexto

A baseline independente do v3 foi congelada antes das correções e permanece registrada em:

`data/evaluation/technical-attributes-v3-baseline.json`

Resultado independente original:

- 45 exemplos;
- 42/45 categorias corretas;
- 86 campos técnicos avaliados;
- 81 campos técnicos corretos;
- micro accuracy de 94,19%;
- 5 falsos negativos técnicos;
- nenhum falso positivo;
- nenhum mismatch.

## Correções aplicadas

A v1.18 trata somente as lacunas registradas no v3:

- `S/VASOCONSTR.` como ausência explícita de vasoconstritor;
- `SEM VASOCONTRITOR` como ausência explícita de vasoconstritor;
- `FOTOATIVADO` e `FOTOATIVADA` como `light_cure`;
- `FOTOPOLIMERIZAVEIS` para modo de cura em descrições plurais;
- `RESINAS FOTOPOLIMERIZAVEIS` como resina composta;
- `RESINA BULK FILL` como resina composta;
- `GEL DE FLUORETO DE SODIO` como flúor em gel.

As regras foram limitadas a formas explícitas para reduzir expansão indevida da taxonomia.

## Resultado pós-tuning

| Métrica | Resultado |
| --- | ---: |
| Exemplos | 45 |
| Categorias corretas | 45/45 |
| Acurácia de categoria | 100,00% |
| Campos técnicos avaliados | 86 |
| Campos técnicos corretos | 86 |
| Micro accuracy | 100,00% |
| Falsos positivos | 0 |
| Falsos negativos | 0 |
| Mismatches | 0 |

Todos os sete atributos avaliados ficaram em 100% neste conjunto congelado.

## Interpretação

Este resultado é regressão pós-tuning, não uma nova estimativa independente de generalização.

As referências independentes continuam sendo:

- 93,33% de acurácia de categoria no v3;
- 94,19% de micro accuracy técnica no v3.

A próxima validação de generalização deve usar fontes novas que não tenham participado dos ciclos v1, v2 ou v3.
