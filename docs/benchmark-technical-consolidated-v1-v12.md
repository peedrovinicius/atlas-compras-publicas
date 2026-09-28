# Consolidação dos benchmarks técnicos v1-v12

## Objetivo

Consolidar as baselines independentes congeladas dos benchmarks técnicos v1 a v12 sem substituir resultados históricos por regressões pós-tuning.

## Cobertura acumulada

Entre v1 e v12 foram avaliados:

- 548 exemplos independentes;
- 984 campos técnicos;
- 485 categorias corretamente classificadas;
- 899 campos técnicos corretamente extraídos;
- 11 falsos positivos técnicos;
- 74 falsos negativos técnicos;
- nenhum mismatch de valor.

Resumo descritivo do conjunto acumulado:

- acurácia de categoria combinada: **88,50%**;
- micro accuracy técnica combinada: **91,36%**.

Os valores agregados resumem holdouts construídos em ciclos distintos e não devem ser interpretados como uma única amostra de produção.

## Baselines independentes

| Benchmark | Parser medido | Exemplos | Acurácia de categoria | Campos | Micro accuracy | FP | FN |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| v1 | 1.12.0 | 33 | 100,00% | 61 | 85,25% | 0 | 9 |
| v2 | 1.14.0 | 41 | 100,00% | 77 | 93,51% | 0 | 5 |
| v3 | 1.16.0 | 45 | 93,33% | 86 | 94,19% | 0 | 5 |
| v4 | 1.18.0 | 45 | 93,33% | 87 | 88,51% | 1 | 9 |
| v5 | 1.20.0 | 48 | 81,25% | 92 | 86,96% | 2 | 10 |
| v6 | 1.22.0 | 48 | 91,67% | 90 | 93,33% | 0 | 6 |
| v7 | 1.24.0 | 48 | 89,58% | 83 | 91,57% | 1 | 6 |
| v8 | 1.26.0 | 48 | 89,58% | 83 | 90,36% | 5 | 3 |
| v9 | 1.28.0 | 48 | 87,50% | 84 | 96,43% | 1 | 2 |
| v10 | 1.30.0 | 48 | 93,75% | 84 | 95,24% | 1 | 3 |
| v11 | 1.32.0 | 48 | 75,00% | 80 | 92,50% | 0 | 6 |
| v12 | 1.34.0 | 48 | 72,92% | 77 | 87,01% | 0 | 10 |

## Leitura técnica

A série não é monotônica por desenho. Cada holdout posterior introduz fontes, redações e dificuldades ainda não usadas no tuning anterior.

O v12 manteve o padrão metodológico da série e aumentou a pressão sobre abreviações, grafias imperfeitas, nomes comerciais, identidades curtas e atributos contextuais. A queda de categoria no v12 não substitui nem invalida resultados anteriores; ela registra dificuldade adicional em um conjunto independente.

## Baseline versus pós-tuning

As baselines independentes medem generalização antes de ajustes específicos do ciclo. Resultados pós-tuning servem para verificar se as lacunas identificadas foram corrigidas sem quebrar regressões protegidas.

Os dois tipos de resultado permanecem separados.

## Arquivos relacionados

- `docs/benchmark-technical-consolidated-v1-v11.md`
- `docs/benchmark-technical-attributes-v12.md`
- `docs/benchmark-technical-attributes-v12-post-tuning.md`
- `docs/dashboard-quality-snapshot.json`
