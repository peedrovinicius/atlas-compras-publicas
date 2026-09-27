# Benchmark independente de atributos técnicos v6

## Objetivo

Medir a generalização das regras técnicas após o tuning contextual da v1.22.

O dataset foi congelado antes da primeira medição.

## Amostra

- 48 descrições públicas;
- 8 contratações inéditas;
- 90 campos técnicos revisados manualmente;
- negativos contextuais com resina;
- produtos genéricos sem atributo técnico explícito;
- anestésicos com e sem vasoconstritor;
- flúor em gel e fluoreto em solução;
- adesivo dual autocondicionante.

## Resultado independente

| Métrica | Resultado |
| --- | ---: |
| Exemplos | 48 |
| Categorias corretas | 44/48 |
| Acurácia de categoria | 91,67% |
| Campos técnicos avaliados | 90 |
| Campos técnicos corretos | 84 |
| Micro accuracy | 93,33% |
| Falsos positivos | 0 |
| Falsos negativos | 6 |
| Mismatches | 0 |

## Resultado por atributo

| Atributo | Avaliados | Corretos | Acurácia |
| --- | ---: | ---: | ---: |
| Tecnologia de resina | 23 | 23 | 100,00% |
| Modo de cura | 32 | 31 | 96,88% |
| Estratégia adesiva | 3 | 3 | 100,00% |
| Uso do ionômero | 5 | 5 | 100,00% |
| Formulação do flúor | 5 | 2 | 40,00% |
| Princípio ativo anestésico | 11 | 10 | 90,91% |
| Vasoconstritor anestésico | 11 | 10 | 90,91% |

## Divergências

### Prilocaína sem a palavra anestésico

A descrição `Prilocaína composição: associada com felipressina` ficou como categoria `unknown`.

A extração técnica de `prilocaine` e `felypressin` não ocorreu porque a categoria não foi reconhecida.

### Fluoreto de sódio em gel

Três descrições usam `Fluoreto De Sódio` com forma farmacêutica em gel e indicação `acidulado` ou `neutro`.

A categoria atual reconhece formas como `FLUOR GEL`, `FLUOR EM GEL` e `GEL DE FLUORETO DE SODIO`, mas não essa ordem textual.

### Ativação dual

O item de adesivo da UFPR usa `tipo: ativação dual`.

A categoria e a estratégia `self_etch` foram reconhecidas, mas o modo de cura não, porque o vocabulário atual usa `CURA DUAL` e `DUAL CURE`.

## Pontos fortes

O v6 não produziu falsos positivos.

Todos os 23 campos de tecnologia de resina ficaram corretos, inclusive em negativos com:

- resina acrílica em dentes artificiais;
- resinas termoplásticas em sugadores;
- pontas para aplicação ou acabamento em resina;
- cimento endodôntico à base de resina epóxica;
- selantes fotopolimerizáveis.

## Interpretação

A baseline v6 recupera desempenho em relação ao v5 e sugere que as regras contextuais da v1.22 generalizam bem para novos negativos de resina.

As seis falhas são concentradas em três formas linguísticas específicas, sem erro contextual positivo.

Esta baseline deve permanecer imutável. Qualquer correção posterior precisa ser registrada como resultado pós-tuning separado.

O holdout v5 da taxonomia continua separado e não foi alterado.
