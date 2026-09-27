# Medicamentos v1 após tuning da v1.44

## Baseline independente preservada

- 48 exemplos;
- 192 campos;
- 168 campos corretos;
- micro accuracy de 87,50%;
- 1 falso positivo;
- 2 falsos negativos;
- 21 mismatches.

## Correções

O tuning foi concentrado em famílias de erro:

- códigos BR e rótulos estruturais do PNCP;
- associações de princípios ativos;
- adjuvantes após concentração;
- concentrações com denominador e separadores de milhar;
- forma `TUBETE`;
- via intravenosa explícita;
- palavras coladas a concentrações;
- uma grafia colada controlada;
- um nome comercial puro que não deve virar princípio ativo.

## Resultado pós-tuning

- 48/48 exemplos;
- 192/192 campos;
- 100% de micro accuracy;
- 0 falsos positivos;
- 0 falsos negativos;
- 0 mismatches.

A baseline de 87,50% permanece imutável.

## Estado do domínio

Medicamentos continua em `benchmark_required`.

Um segundo holdout independente deve ser criado antes de considerar o domínio validado para ativação.
