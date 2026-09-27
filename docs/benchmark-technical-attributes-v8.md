# Benchmark independente de atributos técnicos v8

## Objetivo

Medir a generalização do parser da v1.26 em oito contratações inéditas, usando descrições públicas em trechos fiéis à fonte.

O dataset final foi congelado antes da primeira medição válida.

## Amostra

- 48 descrições;
- 8 contratações inéditas;
- 83 campos técnicos revisados manualmente;
- negativos contextuais;
- abreviação comercial;
- alternativas explícitas;
- marcas de referência no corpo da descrição;
- materiais que contêm termos de outra categoria sem representar o produto correspondente.

## Resultado independente

| Métrica | Resultado |
| --- | ---: |
| Exemplos | 48 |
| Categorias corretas | 43/48 |
| Acurácia de categoria | 89,58% |
| Campos técnicos avaliados | 83 |
| Campos técnicos corretos | 75 |
| Micro accuracy | 90,36% |
| Falsos positivos | 5 |
| Falsos negativos | 3 |
| Mismatches | 0 |

## Resultado por atributo

| Atributo | Avaliados | Corretos | Acurácia |
| --- | ---: | ---: | ---: |
| Tecnologia de resina | 10 | 8 | 80,00% |
| Modo de cura | 34 | 32 | 94,12% |
| Estratégia adesiva | 11 | 10 | 90,91% |
| Uso do ionômero | 7 | 7 | 100,00% |
| Formulação do flúor | 7 | 6 | 85,71% |
| Princípio ativo anestésico | 7 | 5 | 71,43% |
| Vasoconstritor anestésico | 7 | 7 | 100,00% |

## Divergências

### Benzocaína sem a palavra anestésico

Dois itens são descritos diretamente como `Benzocaína ... gel tópico`.

A v1.26 extrai benzocaína quando a categoria já é anestésico local, mas a própria palavra `benzocaína` ainda não participa da identificação da categoria.

Resultado: dois erros de categoria e dois falsos negativos no princípio ativo.

### Abreviação de fotopolimerizável

Um item usa a forma curta `FOTOPOL.` no título do sistema adesivo.

A categoria é reconhecida, mas o modo de cura permanece ausente.

### Alternativa de tecnologia de resina

Duas descrições informam `nanohíbrida ou nanoparticulada`.

O parser seleciona `nanohybrid`, embora a descrição apresente uma alternativa e não determine uma única tecnologia.

### Selante que cita adesivo e ionômero

Um selante fotopolimerizável contém a expressão `ADESIVO PROTETOR DE CIMENTO DE IONÔMERO DE VIDRO`.

A referência subordinada a adesivo faz o produto ser promovido indevidamente à categoria de adesivo e também produz um falso positivo de modo de cura no campo avaliado.

### Marca com a palavra Universal

Um adesivo monocomponente lista `Single Bond Universal` como marca de referência.

A palavra `Universal` é interpretada como estratégia adesiva, apesar de aparecer no nome comercial.

### Flúor com alternativa explícita

A descrição `NEUTRO 2% OU ACIDULADO 1,23%` recebe a formulação `neutral`.

Como há duas alternativas explícitas, o rótulo correto do atributo é indeterminado.

### Cimento de óxido de zinco e eugenol

Um cimento permanente informa `óxido de zinco e eugenol` apenas como composição.

A v1.26 classifica o item como `zinc_oxide`, embora o produto principal seja um cimento combinado fora da taxonomia atual.

### Revelador radiológico

A forma `Revelador Radiológico` não é reconhecida pela regra atual de revelador, que cobre outras variantes lexicais.

## Pontos fortes

O v8 manteve 100% em:

- uso do ionômero;
- vasoconstritor anestésico.

Também permaneceu robusto em negativos contendo fluoreto, resina tixotrópica, ponta adesiva, silano e materiais provisórios.

## Decisão metodológica

Nenhum erro observado no v8 será corrigido na v1.27.

A baseline independente permanece:

- 89,58% de acurácia de categoria;
- 90,36% de micro accuracy técnica.

Qualquer correção deve ocorrer em release posterior e ser registrada como regressão pós-tuning separada.
