# Benchmark v1 da taxonomia

## Objetivo

O benchmark v1 cria uma referência reproduzível para detectar regressões na taxonomia determinística do projeto.

Ele não deve ser interpretado como estimativa independente de desempenho em produção.

## Amostra

A versão v1 contém 37 descrições públicas curtas de itens odontológicos.

As amostras foram rotuladas manualmente e mantêm referência à página pública utilizada na revisão.

Fontes incluídas na v1:

- contratação odontológica de Terra Roxa/SP;
- contratação de Votorantim/SP;
- contratação da UFVJM;
- contratação de Pindoretama/CE publicada diretamente no PNCP.

A amostra cobre 14 rótulos quando `unknown` é incluído.

## Métricas

O comando:

`dpi evaluate-taxonomy --dataset data/evaluation/v1.jsonl`

calcula:

- acurácia global de categoria;
- precision por categoria;
- recall por categoria;
- F1 por categoria;
- macro precision;
- macro recall;
- macro F1;
- acurácia de cor nos exemplos que possuem cor rotulada;
- acurácia de concentração nos exemplos que possuem concentração rotulada.

## Baseline

Código avaliado:

`6800b8a973f29e30389db500bed6575a6fa66c4c`

Resultado:

| Métrica | Resultado |
| --- | ---: |
| Amostras | 37 |
| Acurácia de categoria | 100,00% |
| Macro precision | 1,0000 |
| Macro recall | 1,0000 |
| Macro F1 | 1,0000 |
| Erros de categoria | 0 |
| Cor | 8/8 |
| Concentração | 5/5 |

O arquivo `data/evaluation/v1-baseline.json` registra o snapshot em formato estruturado.

## Por que 100% não significa “modelo perfeito”

As regras foram refinadas usando lacunas observadas nessa própria amostra.

Consequentemente, este resultado mede **consistência sobre casos já revisados**, e não capacidade de generalização para qualquer descrição publicada no PNCP.

Publicar “100% de acurácia” sem essa distinção seria metodologicamente incorreto.

## Uso correto

O benchmark v1 serve para responder:

> Uma alteração nova quebrou classificações que já haviam sido revisadas?

Se a resposta for sim, `evaluation-errors` mostra exatamente os exemplos divergentes e suas fontes.

## Próxima validação

A etapa seguinte deverá criar um dataset v2 com:

1. contratações diferentes das utilizadas para ajustar as regras;
2. rótulos congelados antes da implementação de melhorias;
3. mais exemplos por categoria;
4. categorias ainda não suportadas;
5. casos ambíguos;
6. revisão manual independente quando possível.

Somente uma amostra dessa natureza poderá sustentar uma afirmação mais forte sobre capacidade de generalização.
