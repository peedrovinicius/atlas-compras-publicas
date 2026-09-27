# Benchmark independente de atributos técnicos v10

## Objetivo

Medir a generalização do parser v1.30 em oito novas contratações públicas.

## Resultado independente

| Métrica | Resultado |
| --- | ---: |
| Exemplos | 48 |
| Categorias corretas | 45/48 |
| Acurácia de categoria | 93,75% |
| Campos técnicos avaliados | 84 |
| Campos técnicos corretos | 80 |
| Micro accuracy | 95,24% |
| Falsos positivos | 1 |
| Falsos negativos | 3 |
| Mismatches | 0 |

## Resultado por atributo

| Atributo | Avaliados | Corretos | Acurácia |
| --- | ---: | ---: | ---: |
| Tecnologia de resina | 6 | 6 | 100,00% |
| Modo de cura | 29 | 28 | 96,55% |
| Estratégia adesiva | 6 | 6 | 100,00% |
| Uso do ionômero | 8 | 7 | 87,50% |
| Formulação do flúor | 3 | 2 | 66,67% |
| Princípio ativo anestésico | 16 | 16 | 100,00% |
| Vasoconstritor anestésico | 16 | 15 | 93,75% |

## Divergências

### Cura pela luz em ionômero

Um cimento de ionômero de vidro é descrito como `fotoativao`, `cura pela luz visível` e `fotopolimerização`, sem usar exatamente uma das formas atuais de modo de cura.

A categoria é correta, mas `curing_mode` permanece ausente.

### Flúor tópico acidulado sem forma canônica de gel

A descrição `FLUOR TÓPICO GEL TIXOTRÓPICO (FLUORETO FOSFATO ACIDULADO A 1,23%)` não coincide com as formas de identidade atuais de `fluoride_gel`.

Isso gera erro de categoria e falso negativo de formulação `acidulated`.

### Ionômero reforçado com resina

`IONÔMERO DE VIDRO PÓ E LÍQUIDO RESTAURADOR REFORÇADO C/ RESINA FOTOPOLIMERIZÁVEL` é promovido para resina composta pela referência subordinada a resina.

A categoria deveria continuar sendo ionômero e o uso restaurador deveria ser preservado.

### Cimento obturador com óxido de zinco e eugenol

A descrição `Cimento obturador de canais radiculares a base de óxido de zinco e eugenol` não contém a forma exata `CIMENTO ODONTOLÓGICO` usada pela exclusão atual.

O produto é promovido indevidamente para `zinc_oxide`.

### Vasoconstritores conflitantes

Um item declara `associada com norepinefrina` e, na sequência, especifica `mepivacaína 2% com epinefrina 1:100.000`.

Como a descrição contém duas alternativas incompatíveis, o rótulo técnico é indeterminado. O parser atual escolhe `epinephrine`, produzindo um falso positivo.

## Pontos fortes

O v10 atingiu 100% em:

- tecnologia de resina;
- estratégia adesiva;
- princípio ativo anestésico.

Também manteve 93,75% de acurácia de categoria em um holdout independente com negativos de contexto e descrições contraditórias.

## Decisão metodológica

Nenhum erro observado no v10 será corrigido na v1.31.

A baseline independente permanece:

- 93,75% de acurácia de categoria;
- 95,24% de micro accuracy técnica.

Qualquer melhoria posterior deve ser registrada como regressão pós-tuning separada.
