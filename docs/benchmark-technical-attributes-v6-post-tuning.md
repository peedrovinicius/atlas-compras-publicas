# Atributos técnicos v6 após tuning da v1.24

## Contexto

A baseline independente do v6 permanece registrada em:

`data/evaluation/technical-attributes-v6-baseline.json`

Resultado independente original:

- 48 exemplos;
- 44/48 categorias corretas;
- 90 campos técnicos avaliados;
- 84 campos técnicos corretos;
- micro accuracy de 93,33%;
- 6 falsos negativos;
- nenhum falso positivo;
- nenhum mismatch.

## Correções aplicadas

A v1.24 trata somente os três padrões linguísticos observados no v6:

- `Prilocaína` é reconhecida como anestésico local quando aparece associada explicitamente à felipressina;
- `Fluoreto De Sódio` é reconhecido como gel apenas quando a própria descrição informa `forma farmacêutica` em gel;
- `ativação dual` é reconhecida como `dual_cure` apenas no contexto de adesivo.

Os limites anteriores continuam preservados. `PRILOCAINA 3% SOLUCAO INJETAVEL` e `FLUORETO DE SODIO 2% GEL NEUTRO` permanecem fora dessas novas regras, e `ATIVACAO DUAL` não foi promovida a regra global de cura.

## Validação do escopo

No dataset congelado v6, somente cinco registros entram nas novas regras:

- `ta6-ufes-004`;
- `ta6-ufes-064`;
- `ta6-ufes-066`;
- `ta6-pg-092`;
- `ta6-ufpr-003`.

Esses cinco registros concentram exatamente os seis falsos negativos e os quatro erros de categoria da baseline. Nenhum registro previamente correto entra no novo escopo.

A suíte também passa a exigir regressão integral do dataset v6 em `tests/test_technical_evaluation.py`.

## Resultado pós-tuning

| Métrica | Resultado |
| --- | ---: |
| Exemplos | 48 |
| Categorias corretas | 48/48 |
| Acurácia de categoria | 100,00% |
| Campos técnicos avaliados | 90 |
| Campos técnicos corretos | 90 |
| Micro accuracy | 100,00% |
| Falsos positivos | 0 |
| Falsos negativos | 0 |
| Mismatches | 0 |

## Interpretação

Este resultado é regressão pós-tuning e não substitui a baseline independente.

As referências independentes continuam sendo:

- 91,67% de acurácia de categoria;
- 93,33% de micro accuracy técnica.

O ganho desta etapa é deliberadamente restrito: as novas regras respondem às formas linguísticas observadas no v6 sem ampliar genericamente a taxonomia ou reutilizar a baseline como novo conjunto de treinamento.
