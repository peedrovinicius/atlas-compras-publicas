# Benchmark independente de atributos técnicos v4

## Objetivo

Medir a generalização das regras técnicas após os ciclos de tuning v1.14, v1.16 e v1.18 em fontes totalmente inéditas.

O dataset foi congelado antes da primeira medição.

## Amostra

- 45 descrições públicas;
- 8 contratações inéditas;
- 87 campos técnicos revisados manualmente;
- casos positivos e negativos;
- descrições curtas, comerciais e extensas;
- nenhuma fonte reutilizada dos benchmarks técnicos v1 a v3;
- nenhuma fonte reutilizada dos benchmarks de taxonomia v1 a v5.

## Resultado independente

| Métrica | Resultado |
| --- | ---: |
| Exemplos | 45 |
| Categorias corretas | 42/45 |
| Acurácia de categoria | 93,33% |
| Campos técnicos avaliados | 87 |
| Campos técnicos corretos | 77 |
| Micro accuracy | 88,51% |
| Falsos positivos | 1 |
| Falsos negativos | 9 |
| Mismatches | 0 |

## Resultado por atributo

| Atributo | Avaliados | Corretos | Acurácia |
| --- | ---: | ---: | ---: |
| Tecnologia de resina | 23 | 20 | 86,96% |
| Modo de cura | 33 | 28 | 84,85% |
| Estratégia adesiva | 8 | 7 | 87,50% |
| Uso do ionômero | 2 | 2 | 100,00% |
| Formulação do flúor | 2 | 2 | 100,00% |
| Princípio ativo anestésico | 9 | 9 | 100,00% |
| Vasoconstritor anestésico | 10 | 9 | 90,00% |

## Divergências técnicas

### Abreviação de fotopolimerização

`ADESIVO FOTO` não foi reconhecido como `light_cure`.

### Contexto incorreto de modo de cura

Em `Adesivo para resina fotopolimerizável`, o termo `fotopolimerizável` descreve a resina, não necessariamente o adesivo. O parser atribuiu `light_cure` ao adesivo, gerando o primeiro falso positivo técnico relevante desta série.

### Vasoconstritor

`APINEFRINA`, grafia publicada na fonte, não foi reconhecida como `epinephrine`.

### Estratégia adesiva

`condicionamento acido total` não foi reconhecido porque o vocabulário atual usa `CONDICIONAMENTO TOTAL`.

### Resina fotopolimerizável sem a palavra composta

Três descrições de Nova Veneza usam `Resina fotopolimerizável ... microhibrida`.

Esses itens ficaram como `unknown`, o que impediu também a extração de:

- `microhybrid`;
- `light_cure`.

## Erros de categoria

Os três erros de categoria são os mesmos três itens de Nova Veneza:

- item 162;
- item 163;
- item 164.

A forma `RESINA FOTOPOLIMERIZAVEL` ainda não é uma regra de categoria.

## Interpretação

O v4 é deliberadamente mais adversarial que os conjuntos anteriores.

O resultado independente caiu para 88,51% porque o conjunto adiciona:

- contexto negativo real;
- abreviações comerciais;
- grafia não padronizada;
- descrições onde um atributo aparece ligado a outro produto da frase.

A presença de um falso positivo contextual é especialmente importante, pois mostra que ampliar apenas o vocabulário não é suficiente.

Esta baseline deve permanecer imutável. Qualquer correção posterior precisa ser registrada como resultado pós-tuning separado.

O holdout v5 da taxonomia continua separado e não foi alterado.
