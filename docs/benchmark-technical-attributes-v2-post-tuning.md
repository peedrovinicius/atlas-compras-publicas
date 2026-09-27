# Atributos técnicos v2 após tuning da v1.16

## Contexto

A baseline independente do benchmark técnico v2 permanece preservada em:

`data/evaluation/technical-attributes-v2-baseline.json`

Resultado independente original:

- 41 exemplos;
- 77 campos técnicos avaliados;
- 72 campos corretos;
- micro accuracy de 93,51%;
- 5 falsos negativos;
- nenhum falso positivo;
- nenhum mismatch.

## Correções aplicadas

A v1.16 amplia apenas a extração de atributos técnicos já observados no benchmark v2:

- `QUIMICAMENTE ATIVADO` e `QUIMICAMENTE ATIVADA` para `self_cure`;
- `ACIDULATO` para formulação acidulada;
- `S/VASO` para ausência explícita de vasoconstritor;
- `CIMENTACOES` para uso de cimentação do ionômero.

A taxonomia principal de categorias não foi alterada.

## Resultado pós-tuning

| Métrica | Resultado |
| --- | ---: |
| Exemplos | 41 |
| Campos avaliados | 77 |
| Campos corretos | 77 |
| Micro accuracy | 100,00% |
| Falsos positivos | 0 |
| Falsos negativos | 0 |
| Mismatches | 0 |

Todos os sete atributos avaliados ficaram em 100% neste conjunto congelado.

## Interpretação

Este resultado é uma regressão pós-tuning, não uma nova estimativa independente de generalização.

A referência independente continua sendo 93,51%.

O próximo benchmark técnico deve usar novas fontes que não tenham participado dos ciclos v1 ou v2.
