# Atributos técnicos v8 após tuning da v1.28

## Contexto

A baseline independente do v8 permanece registrada em:

`data/evaluation/technical-attributes-v8-baseline.json`

Resultado independente original:

- 48 exemplos;
- 43/48 categorias corretas;
- 83 campos técnicos avaliados;
- 75 campos técnicos corretos;
- micro accuracy de 90,36%;
- 5 falsos positivos;
- 3 falsos negativos;
- nenhum mismatch.

## Correções aplicadas

A v1.28 trata apenas as lacunas observadas no v8:

- `benzocaína` passa a participar da identificação da categoria de anestésico local;
- `FOTOPOL.` passa a ser reconhecido como abreviação de fotopolimerizável;
- `nanohíbrida ou nanoparticulada` passa a ser tratada como alternativa explícita, sem escolher uma tecnologia única;
- selante que contém referência subordinada a `adesivo protetor` não é promovido à categoria de adesivo;
- conteúdo posterior a `marca de referência` não define estratégia adesiva;
- `neutro ... ou acidulado` não define uma formulação única de flúor;
- cimento odontológico composto por óxido de zinco e eugenol não é reduzido a uma das duas substâncias;
- `Revelador Radiológico` passa a ser reconhecido como revelador radiográfico.

## Limites preservados

As regras foram mantidas restritas ao contexto observado.

- `Single Bond Universal` continua produzindo estratégia `universal` quando faz parte da descrição principal do adesivo, como no benchmark v5;
- óxido de zinco isolado continua classificado como `zinc_oxide`;
- eugenol isolado continua classificado como `eugenol`;
- revelador genérico de placa bacteriana continua fora da categoria radiográfica;
- os holdouts v6, v7 e a baseline v8 permanecem imutáveis.

## Validação do escopo

As novas formas linguísticas atingem os 10 registros únicos que concentram todas as divergências da baseline v8:

- `ta8-vco-016`;
- `ta8-sor-005`;
- `ta8-sor-007`;
- `ta8-sor-009`;
- `ta8-tse-006`;
- `ta8-sjd-007`;
- `ta8-sjd-116`;
- `ta8-ssa-089`;
- `ta8-for-001`;
- `ta8-for-009`.

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
- 90,36% de micro accuracy técnica.

O próximo benchmark técnico deve usar novas contratações e ser congelado antes de qualquer ajuste adicional.
