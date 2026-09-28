# Medicamentos v2 após tuning da v1.46

## Baseline independente preservada

- 48 exemplos;
- 192 campos;
- 153 campos corretos;
- micro accuracy de 79,69%;
- 0 falsos positivos;
- 0 falsos negativos;
- 39 mismatches.

## Tuning controlado

As correções foram agrupadas por comportamento, sem alterar o dataset ou a baseline:

- preservação explícita do separador de associações;
- extração de múltiplos princípios ativos entre concentrações;
- sais e qualificadores em campos estruturados;
- elixir e suspensão oral;
- cápsula abreviada;
- gel vaginal e loção oleosa;
- vias IV, EV e uso tópico explícito;
- normalização limitada de palavras coladas;
- corte de embalagem e percentual fora do ingrediente.

## Regressão protegida

O medicamentos v1 permanece em 192/192 campos corretos.

## Resultado pós-tuning

- medicamentos v2: 192/192 campos;
- micro accuracy: 100%;
- 0 falsos positivos;
- 0 falsos negativos;
- 0 mismatches.

A baseline independente de 79,69% permanece imutável.

O domínio continua em `benchmark_required` até novo holdout independente.
