# Consolidação dos benchmarks de medicamentos v1–v3

## Objetivo

Consolidar a leitura das três primeiras baselines independentes do domínio de medicamentos sem substituir os resultados originais de cada holdout.

Cada benchmark foi congelado antes da primeira medição e medido contra o parser vigente no ciclo correspondente. As regressões pós-tuning são documentadas separadamente e não entram como baseline independente.

## Baselines independentes

| Benchmark | Parser medido | Exemplos | Campos | Corretos | Micro accuracy | Status metodológico |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Medicamentos v1 | v1.40.0 | 48 | 192 | 168 | 87,50% | baseline inicial |
| Medicamentos v2 | v1.44.0 | 48 | 192 | 153 | 79,69% | holdout independente pós-v1 |
| Medicamentos v3 | v1.46.0 | 48 | 192 | 173 | 90,10% | holdout independente pós-v2 |
| **Total ponderado** | — | **144** | **576** | **494** | **85,76%** | visão consolidada |

## Acurácia ponderada por campo

| Campo | Corretos | Total | Acurácia |
| --- | ---: | ---: | ---: |
| Princípio ativo | 94 | 144 | 65,28% |
| Concentração | 137 | 144 | 95,14% |
| Forma farmacêutica | 132 | 144 | 91,67% |
| Via | 131 | 144 | 90,97% |

## Leitura técnica

O acumulado confirma que o gargalo estrutural do domínio continua sendo a extração e normalização do princípio ativo. Concentração, forma farmacêutica e via já apresentam estabilidade muito superior nos três ciclos.

A queda do v2 foi metodologicamente útil porque expôs falhas em associações, sais, pontuação interna e separadores comerciais. O v3 mostrou recuperação da generalização independente, mas ainda não deve ser usado para promover o domínio a estável porque o campo de princípio ativo permanece abaixo do padrão desejado.

## Regressões pós-tuning preservadas

| Ciclo | Resultado pós-tuning | Observação |
| --- | ---: | --- |
| v1 pós-v1.44 | 192/192 | não substitui a baseline v1 |
| v2 pós-v1.46 | 192/192 | não substitui a baseline v2 |
| v3 pós-v1.48 | 192/192 | não substitui a baseline v3 |

## Decisão metodológica

Medicamentos permanece em `benchmark_required`.

A próxima evolução deve ser um **medicamentos v4** totalmente independente, congelado depois da v1.48 e antes de qualquer novo ajuste no parser. O v4 deve priorizar:

- associações com três ou mais princípios ativos;
- sais e qualificadores após vírgula;
- descrições sem forma farmacêutica explícita;
- formas ambíguas entre uso oral, tópico, oftálmico e injetável;
- erros reais de grafia em concentração e forma;
- trechos curtos vindos diretamente da descrição pública da contratação.

## Arquivos relacionados

- `data/evaluation/medications-v1-baseline.json`
- `data/evaluation/medications-v2-baseline.json`
- `data/evaluation/medications-v3-baseline.json`
- `docs/benchmark-medications-v1.md`
- `docs/benchmark-medications-v2.md`
- `docs/benchmark-medications-v3.md`
- `docs/benchmark-medications-v3-post-tuning.md`
