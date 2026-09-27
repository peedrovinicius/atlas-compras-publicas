# Benchmark independente de atributos técnicos v7

## Objetivo

Medir a generalização do parser após o tuning restrito da v1.24 em oito contratações ainda não usadas nos benchmarks técnicos anteriores.

O dataset foi congelado antes da primeira medição no commit `607c9aa9b4089fdadf976a99308cbd90cbd6e865`.

## Amostra

- 48 descrições públicas;
- 8 contratações inéditas;
- 83 campos técnicos revisados manualmente;
- negativos contextuais;
- descrições comerciais curtas;
- erros ortográficos e variações morfológicas;
- benzocaína em anestésico tópico;
- referências subordinadas a outras categorias.

## Resultado independente

| Métrica | Resultado |
| --- | ---: |
| Exemplos | 48 |
| Categorias corretas | 43/48 |
| Acurácia de categoria | 89,58% |
| Campos técnicos avaliados | 83 |
| Campos técnicos corretos | 76 |
| Micro accuracy | 91,57% |
| Falsos positivos | 1 |
| Falsos negativos | 6 |
| Mismatches | 0 |

## Resultado por atributo

| Atributo | Avaliados | Corretos | Acurácia |
| --- | ---: | ---: | ---: |
| Tecnologia de resina | 13 | 13 | 100,00% |
| Modo de cura | 28 | 28 | 100,00% |
| Estratégia adesiva | 9 | 7 | 77,78% |
| Uso do ionômero | 7 | 5 | 71,43% |
| Formulação do flúor | 10 | 10 | 100,00% |
| Princípio ativo anestésico | 8 | 5 | 62,50% |
| Vasoconstritor anestésico | 8 | 8 | 100,00% |

## Divergências

### Benzocaína

Três anestésicos tópicos de benzocaína foram classificados como anestésicos, mas o princípio ativo permaneceu sem extração.

Isso gera três falsos negativos em `anesthetic_active_ingredient`.

### Contexto de adesivo

`Adesivo Para Moldeiras uso: universal` foi interpretado como adesivo dentário restaurador e recebeu a estratégia `universal`.

Esse caso concentra o único falso positivo técnico e também um dos cinco erros de categoria.

Em outro item, `decapagem total` descreve uma estratégia equivalente ao condicionamento total, mas ainda não é reconhecida como `etch_and_rinse`.

### Ionômero: morfologia e contexto

Duas variações de uso não foram extraídas:

- `forração` não foi reconhecida como `liner_base`;
- `restaurações` não foi reconhecida como `restorative`.

Além disso:

- `LONÔMERO DE VIDRO` ficou como categoria `unknown`;
- um selante que apenas menciona `restaurações de ionômero de vidro` foi classificado incorretamente como ionômero.

### Formas genéricas e comerciais

`REVELADOR` isolado não foi suficiente para identificar `radiographic_developer`.

`RESINA FILTEK Z250 XT A1` também ficou como `unknown` porque a descrição comercial não contém uma das formas explícitas atuais de resina composta.

## Pontos fortes

Quatro grupos permaneceram sem erro no v7:

- tecnologia de resina: 13/13;
- modo de cura: 28/28;
- formulação do flúor: 10/10;
- vasoconstritor anestésico: 8/8.

Os negativos envolvendo cariostático, dessensibilizante, pasta profilática, coroa provisória e outros produtos que apenas citam resina ou fluoreto também não geraram falsos positivos nesses atributos.

## Decisão metodológica

Nenhum dos erros observados será corrigido na v1.25.

O v7 permanece como holdout independente da versão 1.24 do parser. Esta baseline é o resultado a ser preservado para futuras comparações.

Qualquer correção deve ocorrer em uma release posterior e ser registrada como regressão pós-tuning separada, sem substituir os valores independentes de 89,58% de categoria e 91,57% de micro accuracy técnica.
