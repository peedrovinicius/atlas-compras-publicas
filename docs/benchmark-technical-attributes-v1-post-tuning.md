# Atributos técnicos v1 após tuning da v1.14

## Contexto

A baseline independente de atributos técnicos foi congelada antes das correções e permanece registrada em:

`data/evaluation/technical-attributes-v1-baseline.json`

Resultado independente original:

- 33 exemplos;
- 61 campos revisados;
- 52 campos corretos;
- micro accuracy de 85,25%;
- 9 falsos negativos;
- nenhum falso positivo.

## Correções aplicadas

A v1.14 amplia apenas a extração de atributos técnicos já observados no benchmark:

- `RESTAURACAO` para uso restaurador de ionômero;
- `SEM VASO` como ausência explícita de vasoconstritor;
- `ACIDULADO` e `NEUTRO` em flúor;
- `UNIVERSAL` em contexto de adesivo;
- `FOTOPOLIMERIZADO` e `FOTOPOLIMERIZADA`;
- `FENILEFRINA`;
- `PRILOCAINA`.

A taxonomia principal de categorias não foi expandida por essas correções.

## Resultado pós-tuning

| Métrica | Resultado |
| --- | ---: |
| Exemplos | 33 |
| Campos avaliados | 61 |
| Campos corretos | 61 |
| Micro accuracy | 100,00% |
| Falsos positivos | 0 |
| Falsos negativos | 0 |
| Mismatches | 0 |

Todos os sete atributos avaliados ficaram em 100% neste conjunto congelado.

## Interpretação

Este resultado é uma regressão pós-tuning, não uma nova estimativa independente de generalização.

A referência independente continua sendo 85,25%.

A próxima avaliação de generalização deve usar novas fontes e descrições que não tenham participado deste ciclo de correção.
