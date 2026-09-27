# Benchmark independente de atributos técnicos v3

## Objetivo

Medir a generalização das regras técnicas após os ciclos de tuning v1.14 e v1.16 usando fontes totalmente inéditas.

O dataset foi congelado antes da primeira medição.

## Amostra

- 45 descrições públicas;
- 8 contratações inéditas;
- 86 campos técnicos revisados manualmente;
- descrições curtas, extensas, abreviadas e com erros de grafia reais;
- nenhuma fonte reutilizada dos benchmarks técnicos v1 e v2;
- nenhuma fonte reutilizada dos benchmarks de taxonomia v1 a v5.

## Resultado independente

| Métrica | Resultado |
| --- | ---: |
| Exemplos | 45 |
| Categorias corretas | 42/45 |
| Acurácia de categoria | 93,33% |
| Campos técnicos avaliados | 86 |
| Campos técnicos corretos | 81 |
| Micro accuracy | 94,19% |
| Falsos positivos | 0 |
| Falsos negativos | 5 |
| Mismatches | 0 |

## Resultado por atributo

| Atributo | Avaliados | Corretos | Acurácia |
| --- | ---: | ---: | ---: |
| Tecnologia de resina | 13 | 12 | 92,31% |
| Modo de cura | 31 | 29 | 93,55% |
| Estratégia adesiva | 9 | 9 | 100,00% |
| Uso do ionômero | 9 | 9 | 100,00% |
| Formulação do flúor | 4 | 4 | 100,00% |
| Princípio ativo anestésico | 10 | 10 | 100,00% |
| Vasoconstritor anestésico | 10 | 8 | 80,00% |

## Divergências técnicas

As cinco divergências técnicas são falsos negativos.

### Ausência de vasoconstritor

Duas grafias não são reconhecidas:

- `S/VASOCONSTR.`;
- `SEM VASOCONTRITOR`.

### Modo de cura

`FOTOATIVADO` ainda não é mapeado para `light_cure`.

Um caso de resina fotopolimerizável também perde o atributo porque a categoria não foi reconhecida.

### Tecnologia de resina

`RESINA BULK FILL` não chega à extração de `bulk_fill` porque a categoria é classificada como `unknown`.

## Erros de categoria

Três descrições ficaram como `unknown`:

- `RESINAS FOTOPOLIMERIZÁVEIS`;
- `RESINA BULK FILL`;
- `GEL DE FLUORETO DE SÓDIO`.

Esses erros são registrados separadamente dos atributos técnicos.

## Interpretação

O v3 melhora a micro accuracy independente de atributos de 93,51% no v2 para 94,19%, mesmo com casos deliberadamente mais difíceis.

Não houve falso positivo nem atributo extraído com valor incorreto.

A baseline deve permanecer imutável. Qualquer correção posterior precisa ser registrada como resultado pós-tuning separado.

O holdout v5 da taxonomia continua separado e não foi alterado.
