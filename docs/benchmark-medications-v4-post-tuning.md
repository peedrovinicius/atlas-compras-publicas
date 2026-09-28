# Medicamentos v4 pós-tuning v1.49

## Objetivo

Registrar a regressão pós-tuning do holdout `medications-v4.jsonl` após uma correção pontual no parser de medicamentos.

Este documento não substitui a baseline independente v4. A baseline preservada continua em `data/evaluation/medications-v4-baseline.json`.

## Correções aplicadas

A versão v1.49.0 alterou apenas dois padrões observados no v4:

1. reconhecimento de `geléia` como forma farmacêutica tópica;
2. remoção de prefixos numéricos compostos, como `6501.266-`, antes do princípio ativo.

Não houve reescrita do dataset.

## Resultado pós-tuning

| Métrica | Valor |
| --- | ---: |
| Exemplos avaliados | 48 |
| Campos avaliados | 192 |
| Campos corretos | 192 |
| Micro accuracy | 100,00% |
| Falsos positivos | 0 |
| Falsos negativos | 0 |
| Mismatches | 0 |

## Resultado por campo

| Campo | Avaliados | Corretos | Acurácia |
| --- | ---: | ---: | ---: |
| Princípio ativo | 48 | 48 | 100,00% |
| Concentração | 48 | 48 | 100,00% |
| Forma farmacêutica | 48 | 48 | 100,00% |
| Via de administração | 48 | 48 | 100,00% |

## Interpretação

O pós-tuning confirma que os três erros da baseline v4 eram residuais e localizados. A correção foi pequena, sem mudança metodológica no holdout e sem alterar os rótulos esperados.

A leitura correta permanece:

- baseline independente v4: 189/192 campos, 98,44%;
- regressão pós-tuning v1.49: 192/192 campos, 100,00%.

## Arquivos relacionados

- `data/evaluation/medications-v4.jsonl`
- `data/evaluation/medications-v4-baseline.json`
- `data/evaluation/medications-v4-post-v1.49.json`
- `docs/benchmark-medications-v4.md`
- `docs/medications-v4-freeze.md`
