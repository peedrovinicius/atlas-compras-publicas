# Ajustes pós-v3: v1.4.0

## Contexto

O benchmark independente v3 registrou 38 acertos em 42 itens, com acurácia de 90,48%.

Os quatro erros foram mantidos intactos no dataset e usados para orientar a v1.4.0.

## Correções

### Variante de óxido de zinco

A taxonomia passa a aceitar tanto:

`OXIDO DE ZINCO`

quanto:

`OXIDO ZINCO`

### Variante de fixador

A categoria `radiographic_fixer` passa a aceitar também:

`FIXADOR RADIOLOGICO`

### Negação explícita

A presença de um termo não é mais considerada evidência positiva quando existe negação explícita.

Exemplos suportados:

- `SEM EUGENOL`;
- `ISENTO DE EUGENOL`;
- `LIVRE DE EUGENOL`;
- `NAO CONTEM EUGENOL`.

Esse mecanismo é genérico para termos avaliados pela taxonomia.

### Kits mistos

Antes da classificação por categoria, o parser verifica se a descrição representa um kit contendo mais de uma família de produto.

Exemplo:

`KIT 3 RESINAS MAIS ADESIVO UNIVERSAL`

Esse caso passa a permanecer como `unknown`, evitando escolher arbitrariamente uma das famílias presentes.

## Revalidação

| Benchmark | Acertos | Total | Acurácia |
| --- | ---: | ---: | ---: |
| v1 | 37 | 37 | 100,00% |
| v2 | 48 | 48 | 100,00% |
| v3 pós-tuning | 42 | 42 | 100,00% |

No v3 pós-tuning:

- macro precision: 1,0000;
- macro recall: 1,0000;
- macro F1: 1,0000.

## Interpretação

O resultado de 100% no v3 é pós-tuning e não deve ser tratado como nova validação independente.

A baseline de 90,48% permanece preservada em `data/evaluation/v3-baseline.json`.

O próximo teste de generalização deve ser um benchmark v4 composto por fontes novas e congelado antes de qualquer ajuste.
