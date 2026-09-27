# Benchmark independente de atributos técnicos v11

## Objetivo

Medir a generalização do parser v1.32 em oito novas contratações públicas.

## Resultado independente

| Métrica | Resultado |
| --- | ---: |
| Exemplos | 48 |
| Categorias corretas | 36/48 |
| Acurácia de categoria | 75,00% |
| Campos técnicos avaliados | 80 |
| Campos técnicos corretos | 74 |
| Micro accuracy | 92,50% |
| Falsos positivos | 0 |
| Falsos negativos | 6 |
| Mismatches | 0 |

## Resultado por atributo

| Atributo | Avaliados | Corretos | Acurácia |
| --- | ---: | ---: | ---: |
| Tecnologia de resina | 9 | 8 | 88,89% |
| Modo de cura | 34 | 32 | 94,12% |
| Estratégia adesiva | 4 | 4 | 100,00% |
| Uso do ionômero | 6 | 4 | 66,67% |
| Formulação do flúor | 3 | 3 | 100,00% |
| Princípio ativo anestésico | 12 | 12 | 100,00% |
| Vasoconstritor anestésico | 12 | 11 | 91,67% |

## Divergências principais

### Abreviação CIV

`CIV RESTAURAÇÕES CLASSE III E V` representa cimento de ionômero de vidro restaurador, mas a regra atual só reconhece formas mais explícitas de `CIV restaurador`.

### Resina descrita apenas por nome e cor

`RESINA A1` é curta demais para as regras atuais de resina composta e fica como `unknown`.

### Fluoreto de sódio em gel

`FLUORETO DE SÓDIO EM GEL` não coincide com as formas atuais da categoria de gel fluoretado.

### Revelador para película

As formas `REVELADOR DE PELÍCULAS` e `REVELADOR PARA FILME RADIOGRÁFICO` não coincidem com os padrões atuais de revelador radiográfico.

### Epinefrina truncada

`EPINEFRIN` não é reconhecida como epinefrina.

### Pontuação dentro da identidade

`IONOMERO, VIDRO` não coincide com as formas atuais de ionômero de vidro.

Isso faz a categoria, uso restaurador e modo de cura do item permanecerem ausentes.

### Hidróxido de cálcio em cimento endodôntico resinoso

Um cimento endodôntico resinoso declara `A BASE HIDROXIDO DE CALCIO`, mas a forma textual não coincide com a expressão canônica `HIDROXIDO DE CALCIO`.

### Óxido de zinco em restaurador temporário

`RESTAURADOR TEMPORARIO ... A BASE DE OXIDO DE ZINCO E EUGENOL` não contém a palavra `cimento`, portanto a exclusão contextual atual não é acionada e o produto é promovido a `zinc_oxide`.

### Resina universal com termo intermediário

`RESINA UNIVERSAL FOTOPOLIMERIZAVEL, MICROHIBRIDA` não coincide com as formas atuais de identidade de resina composta, embora os atributos estejam explicitamente presentes.

## Pontos fortes

O v11 manteve 100% em:

- estratégia adesiva;
- formulação do flúor nos casos avaliados;
- princípio ativo anestésico.

Também não produziu nenhum falso positivo técnico nem mismatch.

## Decisão metodológica

Nenhum erro observado no v11 será corrigido na v1.33.

A baseline independente permanece:

- 75,00% de acurácia de categoria;
- 92,50% de micro accuracy técnica.

Qualquer melhoria posterior deve ser registrada como regressão pós-tuning separada.
