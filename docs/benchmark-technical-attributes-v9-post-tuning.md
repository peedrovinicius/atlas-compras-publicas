# Atributos técnicos v9 após tuning da v1.30

## Contexto

A baseline independente do v9 permanece registrada em:

`data/evaluation/technical-attributes-v9-baseline.json`

Resultado independente original:

- 48 exemplos;
- 42/48 categorias corretas;
- 84 campos técnicos avaliados;
- 81 campos técnicos corretos;
- micro accuracy de 96,43%;
- 1 falso positivo;
- 2 falsos negativos;
- nenhum mismatch.

## Correções aplicadas

A v1.30 trata apenas as lacunas observadas no v9:

- `felilefrina` passa a ser reconhecida como grafia imperfeita de fenilefrina;
- `SEM VASOCONSTRICTOR` passa a ser reconhecido como ausência explícita de vasoconstritor;
- `RESINA - Z250` passa a ser reconhecida como resina composta;
- `IONÔMERO - DE VIDRO` passa a tolerar o hífen interno da descrição;
- `REVELADOR - DENTAL` passa a ser reconhecido como revelador radiográfico;
- óxido de zinco não define a categoria quando aparece dentro de `CIMENTO ODONTOLÓGICO`;
- óxido de zinco em composição base com fosfato de cálcio não define sozinho o produto;
- `CIMENTO ODONTOLÓGICO ... ADESIVO RESINOSO` não é promovido a adesivo restaurador.

## Limites preservados

As correções permanecem contextuais:

- óxido de zinco isolado continua classificado como `zinc_oxide`;
- eugenol isolado continua classificado como `eugenol`;
- cimento com óxido de zinco e eugenol continua fora das categorias isoladas de composição;
- adesivo resinoso sem contexto de cimento continua elegível como adesivo;
- `RESINA FILTEK Z250` continua reconhecida;
- revelador genérico de placa bacteriana continua fora do contexto radiográfico.

## Validação de regressão

O espelho determinístico do parser atualizado foi executado sobre os datasets congelados:

| Dataset | Categorias | Atributos |
| --- | ---: | ---: |
| v8 pós-tuning | 48/48 | 83/83 |
| v9 pós-tuning | 48/48 | 84/84 |

As novas regras atingem os oito registros únicos que concentravam todas as divergências do v9:

- `ta9-bar-012`;
- `ta9-col-1001`;
- `ta9-col-1003`;
- `ta9-col-1014`;
- `ta9-rec-003`;
- `ta9-cbm-007`;
- `ta9-ufe-004`;
- `ta9-ufe-009`.

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

- 87,50% de acurácia de categoria;
- 96,43% de micro accuracy técnica.

O próximo benchmark técnico deve usar novas contratações e ser congelado antes de qualquer ajuste adicional.
