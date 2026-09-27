# Benchmark independente de atributos técnicos v9

## Objetivo

Medir a generalização do parser v1.28 em oito novas contratações públicas.

## Resultado independente

| Métrica | Resultado |
| --- | ---: |
| Exemplos | 48 |
| Categorias corretas | 42/48 |
| Acurácia de categoria | 87,50% |
| Campos técnicos avaliados | 84 |
| Campos técnicos corretos | 81 |
| Micro accuracy | 96,43% |
| Falsos positivos | 1 |
| Falsos negativos | 2 |
| Mismatches | 0 |

## Resultado por atributo

| Atributo | Avaliados | Corretos | Acurácia |
| --- | ---: | ---: | ---: |
| Tecnologia de resina | 7 | 7 | 100,00% |
| Modo de cura | 28 | 27 | 96,43% |
| Estratégia adesiva | 10 | 10 | 100,00% |
| Uso do ionômero | 4 | 4 | 100,00% |
| Formulação do flúor | 3 | 3 | 100,00% |
| Princípio ativo anestésico | 16 | 16 | 100,00% |
| Vasoconstritor anestésico | 16 | 14 | 87,50% |

## Divergências

### Grafia de fenilefrina

A descrição `Anestésico lidocaína com felilefrina` representa uma grafia imperfeita de fenilefrina.

A categoria e a lidocaína são reconhecidas, mas o vasoconstritor não é extraído.

### Forma explícita sem vasoconstritor

A expressão `SEM VASOCONSTRICTOR` não é coberta pela forma atual do padrão negativo, que reconhece variantes próximas mas não essa grafia completa.

Isso gera um falso negativo para o valor `none`.

### Resina Z250 em descrição comercial curta

`RESINA - Z250 XT 4G` não contém as formas explícitas atualmente usadas para identificar resina composta.

### Pontuação interna em ionômero

`IONÔMERO - DE VIDRO` não coincide com a forma normalizada `IONOMERO DE VIDRO` por causa do hífen entre os termos.

### Revelador dental curto

`REVELADOR - DENTAL` não coincide com as formas radiográfica, radiológica ou odontológica atuais.

### Óxido de zinco como componente

Um material em pó lista `OXIDO ZINCO` entre fosfato de cálcio e sulfato de bário.

O parser promove a composição subordinada a categoria `zinc_oxide`.

### Cimento adesivo resinoso

`Cimento Odontológico tipo: adesivo resinoso, ativação: dual` é promovido indevidamente à categoria de adesivo e, por consequência, recebe `dual_cure`.

### Cimento temporário com óxido de zinco

`Cimento Odontológico tipo: temporário, composição: óxido de zinco` é reduzido à categoria `zinc_oxide`, embora o produto principal seja um cimento fora da taxonomia atual.

## Pontos fortes

O v9 atingiu 100% em:

- tecnologia de resina;
- estratégia adesiva;
- uso do ionômero;
- formulação do flúor;
- princípio ativo anestésico.

A micro accuracy técnica subiu para 96,43% em um holdout independente, embora a acurácia de categoria tenha ficado em 87,50%.

## Decisão metodológica

Nenhum erro observado no v9 será corrigido na v1.29.

A baseline independente permanece:

- 87,50% de acurácia de categoria;
- 96,43% de micro accuracy técnica.

Qualquer melhoria posterior deve ser registrada como regressão pós-tuning separada.
