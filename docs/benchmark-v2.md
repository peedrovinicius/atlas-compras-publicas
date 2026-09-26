# Benchmark independente v2

## Objetivo

O benchmark v2 mede o comportamento da taxonomia em descrições que não participaram do desenvolvimento do benchmark v1.

A regra central é simples:

> congelar primeiro, medir depois.

O dataset foi commitado em:

`78780c9e5156426b16e28d7e96f8261f90c660aa`

Nenhuma regra de taxonomia foi alterada entre o congelamento e a medição inicial.

## Fontes

### Itanhaém/SP

PNCP:

`46578498000175-1-000289/2026`

A amostra inclui 24 itens, entre eles adesivo nanoparticulado, cariostático, pasta profilática, resinas microhíbridas, instrumentos e acessórios.

### Araioses/MA

PNCP:

`06450191000170-1-000068/2026`

A amostra inclui 24 itens, entre eles condicionador ácido, adesivo universal, lidocaína, articaína, mepivacaína, anestésico tópico, instrumentos e brocas.

## Resultado

| Métrica | Resultado |
| --- | ---: |
| Amostras | 48 |
| Categorias corretas | 35 |
| Erros | 13 |
| Acurácia | 72,92% |
| Macro precision | 0,6240 |
| Macro recall | 0,5366 |
| Macro F1 | 0,5404 |
| Cor | 7/7 |
| Concentração | 5/5 |

## Resultado por categoria

| Categoria | Suporte | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| composite_resin | 7 | 0,0000 | 0,0000 | 0,0000 |
| dental_adhesive | 2 | 0,0000 | 0,0000 | 0,0000 |
| local_anesthetic | 4 | 1,0000 | 0,2500 | 0,4000 |
| phosphoric_acid | 1 | 1,0000 | 1,0000 | 1,0000 |
| prophylaxis_paste | 1 | 1,0000 | 1,0000 | 1,0000 |
| unknown | 33 | 0,7442 | 0,9697 | 0,8421 |

## Erros observados

### Resina microhíbrida

Sete itens esperados como `composite_resin` foram classificados como `unknown`.

A taxonomia atual reconhece expressões como “resina composta”, mas ainda não trata “resina microhíbrida” como evidência suficiente por si só.

### Adesivos

Dois adesivos falharam.

Um deles ficou como `unknown` por trazer palavras intermediárias entre “adesivo” e “fotopolimerizável”.

Outro foi classificado incorretamente como resina porque a descrição do adesivo mencionava “resina composta” no contexto de uso.

Esse caso expõe uma limitação importante das regras puramente baseadas em ocorrência de termos.

### Anestésicos

Lidocaína, articaína e mepivacaína, quando descritas diretamente pelo princípio ativo, não foram reconhecidas.

O anestésico tópico com a palavra explícita “anestésico” foi corretamente classificado.

### Falso positivo contextual

Um kit de acabamento e polimento foi classificado como `composite_resin` apenas porque a descrição continha “resina composta”.

Isso mostra a necessidade de diferenciar **o produto comprado** de **o produto sobre o qual ele é utilizado**.

## Interpretação

O v2 é mais informativo que o v1 para generalização.

O resultado de 72,92% não deve ser escondido ou corrigido retroativamente. Ele estabelece a baseline independente sobre a qual melhorias futuras poderão ser comparadas.

A próxima versão poderá usar esses 13 erros para melhorar a taxonomia, mas os rótulos do v2 permanecerão congelados.

Depois das melhorias, um terceiro benchmark com fontes novas deverá ser criado para evitar novo overfitting.

## Reprodutibilidade

~~~bash
dpi evaluate-taxonomy --dataset data/evaluation/v2.jsonl
dpi evaluation-errors --dataset data/evaluation/v2.jsonl
~~~
