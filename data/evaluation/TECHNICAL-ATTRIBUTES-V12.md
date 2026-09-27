# Dataset independente de atributos técnicos v12

O arquivo `technical-attributes-v12.jsonl` foi congelado antes da primeira medição no commit `a11ac27890ee46269cb0e830786ba4dbd3545bfa`.

## Objetivo

Medir a generalização do parser após o tuning da v1.34 em oito contratações inéditas.

## Composição

- 48 exemplos;
- 8 contratações inéditas;
- 77 campos técnicos revisados;
- 6 exemplos por contratação;
- abreviações e grafias reais como `RX`, `SV`, `Z100`, `AUTO-CONDICIONANTE` e `FENILEFINA`;
- positivos e negativos contextuais.

## Regra metodológica

A primeira medição ocorreu somente após o congelamento do dataset.

O espelho determinístico da v1.34 foi validado antes contra o v11 pós-tuning e reproduziu exatamente 48/48 categorias e 80/80 campos técnicos.

Nenhuma lacuna do v12 será corrigida na v1.35.
