# Medicamentos v3 após tuning da v1.48

## Baseline independente preservada

- 48 exemplos;
- 192 campos;
- 173 campos corretos;
- micro accuracy de 90,10%;
- 0 falsos positivos;
- 5 falsos negativos;
- 14 mismatches.

## Tuning controlado

As correções foram agrupadas por padrão:

- `PRINCIPIO ATIVO: sal ...`;
- sais descritos em `COMPOSICAO`;
- associações com `ASSOCIADO COM` e `ASSOCIADO C/`;
- associações múltiplas;
- vírgula entre fármaco e sulfato;
- abreviações `SOL INJ` e `PO PARA SOL INJ`;
- `PO PARA SUSPENSAO`;
- `VIA DE ADMINISTRACAO TOPICA`;
- forma tópica genérica `GEL`;
- correção lexical restrita de `CONCETRACAO`;
- corte de marcadores de forma misturados ao princípio ativo.

## Regressões protegidas

- medicamentos v1: 192/192;
- medicamentos v2: 192/192;
- medicamentos v3: 192/192.

## Resultado pós-tuning

- micro accuracy: 100%;
- 0 falsos positivos;
- 0 falsos negativos;
- 0 mismatches.

A baseline independente de 90,10% permanece imutável.

## Estado do domínio

Medicamentos continua em `benchmark_required`.

A próxima decisão metodológica deve usar um novo holdout v4, congelado depois desta release e antes de qualquer nova medição.
