# Consolidação dos benchmarks de medicamentos v1–v4

## Objetivo

Consolidar a leitura das quatro baselines independentes do domínio de medicamentos sem substituir os resultados originais de cada holdout.

Cada benchmark foi congelado antes da primeira medição e medido contra o parser vigente no ciclo correspondente. As regressões pós-tuning são documentadas separadamente e não entram como baseline independente.

## Baselines independentes

| Benchmark | Parser medido | Exemplos | Campos | Corretos | Micro accuracy | Status metodológico |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Medicamentos v1 | v1.40.0 | 48 | 192 | 168 | 87,50% | baseline inicial |
| Medicamentos v2 | v1.44.0 | 48 | 192 | 153 | 79,69% | holdout independente pós-v1 |
| Medicamentos v3 | v1.46.0 | 48 | 192 | 173 | 90,10% | holdout independente pós-v2 |
| Medicamentos v4 | pós-v1.48 vigente | 48 | 192 | 189 | 98,44% | holdout independente pós-v3 |
| **Total ponderado** | — | **192** | **768** | **683** | **88,93%** | visão consolidada |

## Acurácia ponderada por campo

| Campo | Corretos | Total | Acurácia |
| --- | ---: | ---: | ---: |
| Princípio ativo | 141 | 192 | 73,44% |
| Concentração | 185 | 192 | 96,35% |
| Forma farmacêutica | 179 | 192 | 93,23% |
| Via | 178 | 192 | 92,71% |

## Leitura técnica

O v4 elevou a leitura consolidada do domínio para 683 campos corretos em 768 avaliados, com micro accuracy ponderada de 88,93%.

O principal ganho aparece na estabilidade do holdout independente mais recente. O v4 teve 189 de 192 campos corretos, com apenas três mismatches. Ainda assim, a consolidação preserva a leitura histórica: princípio ativo continua sendo o campo mais sensível quando acumulamos todos os ciclos.

## Erros remanescentes da baseline v4

| ID | Campo | Esperado | Predito | Interpretação |
| --- | --- | --- | --- | --- |
| `med4-cur93-020` | `dosage_form` | `topical` | `unknown` | `geléia` ainda não era reconhecida como forma tópica. |
| `med4-cur93-020` | `route` | `topical` | `unknown` | Erro derivado da forma farmacêutica não reconhecida. |
| `med4-cur1270-001` | `active_ingredient` | `AMOXICILINA TRIIDRATADA` | `.266-AMOXICILINA TRIIDRATADA` | Prefixo numérico composto deixou resíduo antes do princípio ativo. |

## Regressões pós-tuning preservadas

| Ciclo | Resultado pós-tuning | Observação |
| --- | ---: | --- |
| v1 pós-v1.44 | 192/192 | não substitui a baseline v1 |
| v2 pós-v1.46 | 192/192 | não substitui a baseline v2 |
| v3 pós-v1.48 | 192/192 | não substitui a baseline v3 |
| v4 pós-v1.49 | 192/192 | não substitui a baseline v4 |

O pós-tuning v1.49 corrigiu os três erros residuais do v4 com duas mudanças pequenas: reconhecimento de `geléia` como forma tópica e remoção de prefixos numéricos compostos.

## Decisão metodológica

Medicamentos permanece em `benchmark_required` na leitura consolidada porque a decisão de promoção deve considerar a série histórica das baselines independentes, não apenas regressões pós-tuning perfeitas.

Não há indicação para tuning amplo. A evolução v1.49 foi pontual e deve ser mantida separada da baseline independente.

## Arquivos relacionados

- `data/evaluation/medications-v1-baseline.json`
- `data/evaluation/medications-v2-baseline.json`
- `data/evaluation/medications-v3-baseline.json`
- `data/evaluation/medications-v4-baseline.json`
- `data/evaluation/medications-v4-post-v1.49.json`
- `docs/benchmark-medications-v1.md`
- `docs/benchmark-medications-v2.md`
- `docs/benchmark-medications-v3.md`
- `docs/benchmark-medications-v4.md`
- `docs/benchmark-medications-v4-post-tuning.md`
- `docs/medications-v4-freeze.md`
