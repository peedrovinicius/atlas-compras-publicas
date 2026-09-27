# Benchmark independente de atributos técnicos v2

## Objetivo

Medir a generalização das regras de atributos técnicos após o tuning da v1.14 em fontes totalmente novas.

O dataset foi congelado antes da primeira medição.

## Amostra

- 41 descrições públicas;
- 8 contratações inéditas;
- 77 campos técnicos revisados manualmente;
- 41/41 categorias corretas;
- campos positivos e negativos;
- nenhuma fonte reutilizada dos benchmarks técnicos ou de taxonomia anteriores.

## Resultado independente

| Métrica | Resultado |
| --- | ---: |
| Exemplos | 41 |
| Categorias corretas | 41/41 |
| Campos técnicos avaliados | 77 |
| Campos técnicos corretos | 72 |
| Micro accuracy | 93,51% |
| Falsos positivos | 0 |
| Falsos negativos | 5 |
| Mismatches | 0 |

## Resultado por atributo

| Atributo | Avaliados | Corretos | Acurácia |
| --- | ---: | ---: | ---: |
| Tecnologia de resina | 10 | 10 | 100,00% |
| Modo de cura | 23 | 21 | 91,30% |
| Estratégia adesiva | 6 | 6 | 100,00% |
| Uso do ionômero | 8 | 7 | 87,50% |
| Formulação do flúor | 3 | 2 | 66,67% |
| Princípio ativo anestésico | 14 | 14 | 100,00% |
| Vasoconstritor anestésico | 13 | 12 | 92,31% |

## Divergências observadas

As cinco divergências são falsos negativos. Não houve atributo inventado nem valor técnico incorreto.

### Modo de cura

Dois ionômeros usam a expressão `QUIMICAMENTE ATIVADO`, ainda não mapeada para `self_cure`.

### Formulação do flúor

Um item usa a variante `ACIDULATO`, diferente de `ACIDULADO`.

### Ausência de vasoconstritor

Um anestésico usa a abreviação `S/VASO`, ainda não reconhecida como ausência explícita.

### Uso do ionômero

Um item usa `CIMENTACOES`, forma plural que não coincide com o vocabulário atual.

## Regra metodológica

Esta baseline deve permanecer imutável.

As cinco lacunas podem orientar um ciclo posterior de tuning, mas qualquer resultado após ajuste deve ser salvo em artefato separado.

O benchmark técnico v1 e o holdout v5 da taxonomia permanecem independentes deste conjunto.


## Resultado posterior

A v1.16 corrigiu as cinco lacunas observadas e atingiu 77/77 no mesmo conjunto.

Esse valor é registrado separadamente como regressão pós-tuning em `docs/benchmark-technical-attributes-v2-post-tuning.md` e não substitui a baseline independente de 93,51%.
