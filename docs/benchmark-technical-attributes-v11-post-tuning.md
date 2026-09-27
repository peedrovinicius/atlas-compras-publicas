# Atributos técnicos v11 após tuning da v1.34

## Contexto

A baseline independente do v11 permanece registrada em `data/evaluation/technical-attributes-v11-baseline.json`.

Resultado independente original:

- 48 exemplos;
- 36/48 categorias corretas;
- 80 campos técnicos avaliados;
- 74 campos técnicos corretos;
- micro accuracy de 92,50%;
- 0 falsos positivos;
- 6 falsos negativos;
- nenhum mismatch.

## Correções aplicadas

A v1.34 trata apenas as lacunas observadas no v11:

- `CIV RESTAURAÇÕES` passa a ser reconhecido como ionômero restaurador;
- `RESINA A1` e `RESINA UNIVERSAL` passam a ser reconhecidas como resina composta em seus contextos específicos;
- `FLUORETO DE SÓDIO EM GEL` passa a ser reconhecido como gel fluoretado;
- formas de revelador e fixador descritas por película/filme radiográfico passam a ser reconhecidas;
- `EPINEFRIN` passa a ser reconhecida como epinefrina;
- `IONOMERO, VIDRO` passa a tolerar a pontuação interna;
- `A BASE HIDROXIDO DE CALCIO` recebe precedência sobre a regra de kit misto;
- restaurador temporário à base de óxido de zinco e eugenol não é reduzido a uma das substâncias isoladas.

## Validação de regressão

| Dataset | Categorias | Atributos |
| --- | ---: | ---: |
| v10 pós-tuning | 48/48 | 84/84 |
| v11 pós-tuning | 48/48 | 80/80 |

## Resultado pós-tuning

| Métrica | Resultado |
| --- | ---: |
| Exemplos | 48 |
| Categorias corretas | 48/48 |
| Acurácia de categoria | 100,00% |
| Campos técnicos avaliados | 80 |
| Campos técnicos corretos | 80 |
| Micro accuracy | 100,00% |
| Falsos positivos | 0 |
| Falsos negativos | 0 |
| Mismatches | 0 |

Este resultado não substitui a baseline independente de 75,00% em categoria e 92,50% em atributos.
