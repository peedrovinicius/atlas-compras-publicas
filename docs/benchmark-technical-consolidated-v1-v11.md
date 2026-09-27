# Consolidação dos benchmarks técnicos v1–v11

## Objetivo

Este documento consolida exclusivamente as **baselines independentes congeladas** dos benchmarks técnicos v1 a v11.

Resultados pós-tuning não substituem as baselines e não são usados para calcular os números agregados abaixo.

## Cobertura acumulada

Entre v1 e v11 foram avaliados:

- 500 exemplos independentes;
- 907 campos técnicos;
- 450 categorias corretamente classificadas;
- 832 campos técnicos corretamente extraídos;
- 11 falsos positivos técnicos;
- 64 falsos negativos técnicos;
- nenhum mismatch de valor.

Como resumo descritivo do conjunto acumulado:

- acurácia de categoria combinada: **90,00%**;
- micro accuracy técnica combinada: **91,73%**.

Esses valores agregados não representam uma única amostra i.i.d. e não devem ser interpretados como estimativa estatística de produção. Cada geração foi construída com fontes, redações e dificuldades diferentes.

## Baselines independentes

| Benchmark | Parser medido | Exemplos | Acurácia de categoria | Campos | Micro accuracy | FP | FN |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| v1 | 1.12.0 | 33 | 100,00% | 61 | 85,25% | 0 | 9 |
| v2 | 1.14.0 | 41 | 100,00% | 77 | 93,51% | 0 | 5 |
| v3 | 1.16.0 | 45 | 93,33% | 86 | 94,19% | 0 | 5 |
| v4 | 1.18.0 | 45 | 93,33% | 87 | 88,51% | 1 | 9 |
| v5 | 1.20.0 | 48 | 81,25% | 92 | 86,96% | 2 | 10 |
| v6 | 1.22.0 | 48 | 91,67% | 90 | 93,33% | 0 | 6 |
| v7 | 1.24.0 | 48 | 89,58% | 83 | 91,57% | 1 | 6 |
| v8 | 1.26.0 | 48 | 89,58% | 83 | 90,36% | 5 | 3 |
| v9 | 1.28.0 | 48 | 87,50% | 84 | 96,43% | 1 | 2 |
| v10 | 1.30.0 | 48 | 93,75% | 84 | 95,24% | 1 | 3 |
| v11 | 1.32.0 | 48 | 75,00% | 80 | 92,50% | 0 | 6 |

## Como interpretar a série

A série **não é monotônica por desenho**.

Uma queda de acurácia em uma versão posterior não significa necessariamente regressão do parser. Os holdouts posteriores introduzem deliberadamente novas fontes, abreviações, erros de grafia, marcas comerciais, contexto subordinado, alternativas explícitas e descrições mais curtas.

Exemplos:

- v1 e v2 tinham categoria perfeita, mas os conjuntos eram menos adversariais na identidade;
- v5 reduziu a acurácia de categoria para 81,25% ao introduzir mais abreviações e negativos contextuais;
- v9 alcançou 96,43% nos atributos, mas ainda manteve erros de identidade;
- v11 caiu para 75,00% em categoria com formas extremamente curtas como `CIV`, `RESINA A1` e revelador descrito por película.

O valor principal da série é medir **generalização fora do conjunto que originou o tuning anterior**, não criar uma sequência de números crescentes.

## Evolução metodológica

### v1–v4

As primeiras gerações estabeleceram o ciclo de:

1. congelar dataset;
2. medir parser sem tuning;
3. registrar erros por atributo;
4. corrigir em release posterior.

### v5–v7

Os conjuntos passaram a enfatizar:

- negativos contextuais;
- abreviações comerciais;
- erros de grafia;
- tecnologias alternativas;
- separação explícita entre baseline e resultado pós-tuning.

### v8–v11

A metodologia ficou mais rígida:

- trechos fiéis às descrições públicas;
- fontes de contratação ainda não usadas;
- validação do espelho determinístico contra o holdout anterior pós-tuning;
- baseline histórica imutável;
- artefato pós-tuning separado;
- auditoria de escopo das regras antes do merge.

## Padrão de erro observado

Ao longo da série, os erros deixaram de ser majoritariamente ausência de termos técnicos comuns e passaram a se concentrar em:

- variações ortográficas e abreviações;
- separadores e pontuação inseridos no nome do produto;
- termos técnicos presentes apenas como composição subordinada;
- nomes comerciais;
- ambiguidades e alternativas explícitas;
- precedência entre categoria principal e componentes;
- descrições extremamente curtas.

Isso indica que o próximo ganho estrutural não virá apenas da adição de aliases. O motor precisa separar de forma mais explícita normalização lexical, evidência de identidade, contexto e resolução de ambiguidade.

## Baseline versus pós-tuning

Uma baseline independente responde:

> Como o parser generaliza para dados que ainda não participaram do ajuste?

Um resultado pós-tuning responde:

> As lacunas daquele conjunto foram corrigidas sem quebrar as regressões protegidas?

Esses dois números têm finalidades diferentes e nunca devem ser misturados.

## Regra para próximas gerações

Para qualquer benchmark técnico futuro:

1. usar contratações ainda não presentes nos holdouts anteriores;
2. preservar descrição fiel à fonte;
3. congelar dataset e rótulos antes da primeira medição;
4. registrar SHA do dataset e do parser;
5. medir sem alterar o parser;
6. preservar a baseline permanentemente;
7. fazer tuning apenas em release posterior;
8. registrar pós-tuning em artefato separado;
9. executar regressão sobre holdouts anteriores relevantes;
10. documentar qualquer mudança metodológica.

## Corte desta consolidação

Este relatório consolida **v1 a v11**.

O v12 foi criado posteriormente como novo holdout independente e permanece fora dos agregados deste documento para preservar o corte metodológico solicitado.
