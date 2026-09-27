# Benchmark independente de atributos técnicos v1

## Objetivo

Medir a extração de atributos técnicos em descrições públicas que não participaram do desenvolvimento das regras atuais.

O dataset foi congelado antes da primeira medição. O holdout v5 da taxonomia permanece separado e não foi usado para ajustar esta etapa.

## Amostra

- 33 descrições públicas;
- 8 contratações novas em relação aos benchmarks v1 a v5;
- 61 campos técnicos revisados manualmente;
- campos positivos e negativos explicitamente rotulados;
- URLs e números de controle preservados no dataset.

## Baseline

A medição foi feita contra as regras do parser v1.12.0, antes de qualquer ajuste motivado por este conjunto.

| Métrica | Resultado |
| --- | ---: |
| Exemplos | 33 |
| Categorias corretas | 33/33 |
| Campos técnicos avaliados | 61 |
| Campos técnicos corretos | 52 |
| Micro accuracy | 85,25% |
| Falsos positivos | 0 |
| Falsos negativos | 9 |
| Mismatches | 0 |

## Resultado por atributo

| Atributo | Avaliados | Corretos | Acurácia |
| --- | ---: | ---: | ---: |
| Tecnologia de resina | 5 | 5 | 100,00% |
| Modo de cura | 15 | 14 | 93,33% |
| Estratégia adesiva | 4 | 3 | 75,00% |
| Uso do ionômero | 4 | 2 | 50,00% |
| Formulação do flúor | 3 | 1 | 33,33% |
| Princípio ativo anestésico | 15 | 14 | 93,33% |
| Vasoconstritor anestésico | 15 | 13 | 86,67% |

## Divergências observadas

As nove divergências são falsos negativos. Nenhum campo foi extraído com valor incorreto e nenhum atributo ausente foi inventado.

### Ionômero

Dois casos usam a forma `RESTAURACAO`, enquanto a regra atual reconhece `RESTAURADOR` e `RESTAURATIVO`.

### Vasoconstritor ausente

`SEM VASO` não é reconhecido como ausência explícita de vasoconstritor.

### Formulação do flúor

Descrições com `ACIDULADO` ou `NEUTRO` sem as formas compostas atualmente previstas não são extraídas.

### Adesivo

`ADESIVO DENTINARIO UNIVERSAL` não coincide com a forma atual `ADESIVO UNIVERSAL`.

O mesmo item usa `FOTOPOLIMERIZADO`, forma ainda não reconhecida para modo de cura.

### Anestésicos

`FENILEFRINA` ainda não existe no vocabulário de vasoconstritores.

`PRILOCAINA` ainda não existe no vocabulário de princípios ativos.

## Regra metodológica

Esta baseline não deve ser sobrescrita.

Melhorias futuras podem ser medidas contra o mesmo conjunto, mas precisam ser registradas como resultado pós-tuning separado. O arquivo `technical-attributes-v1-baseline.json` preserva a medição independente original.

## Execução

~~~bash
dpi evaluate-technical-attributes \
  --dataset data/evaluation/technical-attributes-v1.jsonl
~~~

Para listar somente divergências:

~~~bash
dpi technical-attribute-errors \
  --dataset data/evaluation/technical-attributes-v1.jsonl
~~~


## Resultado posterior

A v1.14 corrigiu as nove lacunas observadas e atingiu 61/61 no mesmo conjunto.

Esse valor é registrado separadamente como regressão pós-tuning em `docs/benchmark-technical-attributes-v1-post-tuning.md` e não substitui a baseline independente de 85,25%.
