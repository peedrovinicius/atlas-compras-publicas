# Benchmark de medicamentos v4

## Objetivo

Registrar a primeira medição do parser vigente contra o holdout independente `medications-v4.jsonl`.

O dataset foi congelado antes da execução da baseline. Nenhuma regra do parser foi alterada durante a construção do v4 ou antes desta medição.

## Dataset

| Campo | Valor |
| --- | ---: |
| Arquivo | `data/evaluation/medications-v4.jsonl` |
| Exemplos | 48 |
| Campos por exemplo | 4 |
| Campos avaliados | 192 |
| Fontes públicas | 8 |
| Status | holdout independente congelado |

Campos avaliados:

- `active_ingredient`
- `strength`
- `dosage_form`
- `route`

## Resultado geral

| Métrica | Valor |
| --- | ---: |
| Exemplos avaliados | 48 |
| Campos avaliados | 192 |
| Campos corretos | 189 |
| Micro accuracy | 98,44% |
| Falsos positivos | 0 |
| Falsos negativos | 0 |
| Mismatches | 3 |

## Resultado por campo

| Campo | Avaliados | Corretos | Acurácia | Mismatches |
| --- | ---: | ---: | ---: | ---: |
| Princípio ativo | 48 | 47 | 97,92% | 1 |
| Concentração | 48 | 48 | 100,00% | 0 |
| Forma farmacêutica | 48 | 47 | 97,92% | 1 |
| Via de administração | 48 | 47 | 97,92% | 1 |

## Erros observados

| ID | Campo | Esperado | Predito | Leitura técnica |
| --- | --- | --- | --- | --- |
| `med4-cur93-020` | `dosage_form` | `topical` | `unknown` | O parser não reconheceu `geléia` como marcador tópico equivalente a gel. |
| `med4-cur93-020` | `route` | `topical` | `unknown` | A via dependeu da forma farmacêutica; como `geléia` não foi reconhecida, a via também ficou desconhecida. |
| `med4-cur1270-001` | `active_ingredient` | `AMOXICILINA TRIIDRATADA` | `.266-AMOXICILINA TRIIDRATADA` | O prefixo `6501.266-` deixou resíduo `.266-` após a remoção parcial do código inicial. |

## Interpretação

O v4 confirma alta estabilidade do parser no domínio de medicamentos, com 189 de 192 campos corretos.

O melhor resultado foi em concentração, com 48 de 48 campos corretos. Os erros restantes não indicam regressão ampla do domínio. Eles estão concentrados em dois padrões específicos:

1. forma farmacêutica tópica escrita como `geléia`;
2. prefixo de código composto com ponto antes do nome do medicamento.

## Decisão sobre tuning

Não há necessidade de tuning amplo do parser.

Caso haja uma versão posterior, ela deve ser pequena e direcionada para:

- reconhecer `geléia` como forma tópica quando usada em descrição farmacêutica;
- remover prefixos numéricos compostos do tipo `6501.266-` sem deixar resíduo antes do princípio ativo.

A baseline v4 deve permanecer preservada. Qualquer melhoria posterior precisa ser registrada em arquivo separado de pós-tuning, sem substituir `medications-v4-baseline.json`.

## Arquivos relacionados

- `data/evaluation/medications-v4.jsonl`
- `data/evaluation/medications-v4-baseline.json`
- `docs/medications-v4-freeze.md`
- `docs/medications-v4-item-triage.md`
- `docs/benchmark-medications-v4-plan.md`
