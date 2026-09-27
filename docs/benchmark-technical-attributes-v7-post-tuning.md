# Atributos técnicos v7 após tuning da v1.26

## Contexto

A baseline independente do v7 permanece registrada em:

`data/evaluation/technical-attributes-v7-baseline.json`

Resultado independente original:

- 48 exemplos;
- 43/48 categorias corretas;
- 83 campos técnicos avaliados;
- 76 campos técnicos corretos;
- micro accuracy de 91,57%;
- 1 falso positivo;
- 6 falsos negativos;
- nenhum mismatch.

## Correções aplicadas

A v1.26 trata apenas as lacunas observadas no v7:

- `benzocaína` passa a ser extraída como princípio ativo quando o item já foi identificado como anestésico local;
- `adesivo para moldeira` é excluído da identidade de adesivo dentário restaurador;
- `decapagem total` passa a representar a estratégia `etch_and_rinse`;
- `forração` é reconhecida como `liner_base`;
- `restaurações` é reconhecida como uso restaurador quando o produto principal já é ionômero;
- o erro gráfico `LONÔMERO DE VIDRO` é tratado como forma explícita de ionômero;
- `REVELADORREVELADOR` é tratado como a duplicação textual observada no item de revelador radiográfico;
- selante que apenas menciona restaurações de ionômero não é promovido a ionômero;
- `RESINA FILTEK Z250` é reconhecida como forma comercial explícita de resina composta.

## Limites preservados

As regras foram mantidas restritas ao contexto observado.

- `BENZOCAINA 20% GEL` sem identidade de anestésico não passa a definir categoria por si só;
- `REVELADOR` genérico não vira automaticamente revelador radiográfico;
- adesivo dentário universal continua classificado como adesivo;
- resina Filtek Bulk Fill Flow continua sendo classificada como resina fluida;
- selante que cita ionômero continua fora da categoria de ionômero.

## Validação do escopo

As novas regras atingem exatamente os 11 registros que concentram os erros da baseline v7:

- `ta7-bg-009`;
- `ta7-ib-009`;
- `ta7-na-009`;
- `ta7-sr-001`;
- `ta7-sr-005`;
- `ta7-sr-027`;
- `ta7-sr-073`;
- `ta7-dd-051`;
- `ta7-ca-061`;
- `ta7-ca-121`;
- `ta7-ma-4049`.

Nenhum outro exemplo do holdout entra no novo escopo.

## Resultado pós-tuning

| Métrica | Resultado |
| --- | ---: |
| Exemplos | 48 |
| Categorias corretas | 48/48 |
| Acurácia de categoria | 100,00% |
| Campos técnicos avaliados | 83 |
| Campos técnicos corretos | 83 |
| Micro accuracy | 100,00% |
| Falsos positivos | 0 |
| Falsos negativos | 0 |
| Mismatches | 0 |

## Interpretação

Este resultado é regressão pós-tuning e não substitui a baseline independente.

As referências independentes continuam sendo:

- 89,58% de acurácia de categoria;
- 91,57% de micro accuracy técnica.

A v1.26 corrige o conjunto congelado sem reescrever a medição original. O próximo benchmark técnico deve usar novas contratações e ser congelado antes de qualquer ajuste adicional.
