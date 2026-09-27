# Dataset independente de atributos técnicos v2

O arquivo `technical-attributes-v2.jsonl` foi congelado antes da primeira medição.

## Objetivo

Testar a generalização das regras de atributos técnicos após o ciclo de tuning da v1.14.

Nenhuma contratação deste conjunto foi usada nos benchmarks de taxonomia v1 a v5 ou no benchmark técnico v1.

## Fontes

- Adamantina/SP, PNCP `43008291000177-1-000076/2026`;
- Teresina/PI, PNCP `05522917000170-1-000157/2026`;
- Monte Horebe/PB, PNCP `08924011000170-1-000037/2026`;
- Olivença/AL, PNCP `12257762000157-1-000016/2026`;
- Marabá Paulista/SP, PNCP `45725355000186-1-000023/2026`;
- Iguaraçu/PR, PNCP `75772525000144-1-000115/2026`;
- Aracruz/ES, PNCP `10429253000139-1-000026/2026`;
- Cafeara/PR, PNCP `75845545000106-1-000030/2026`.

## Composição

- 41 exemplos;
- 8 contratações inéditas;
- campos positivos e negativos;
- URLs e números de controle preservados;
- rótulos baseados somente em informação explícita na descrição;
- nenhum ajuste de regra entre o congelamento e a primeira medição.

## Regra metodológica

A primeira medição deve ser registrada antes de qualquer tuning.

Se houver erros, o dataset permanece imutável e qualquer melhoria posterior deve ser publicada em artefato separado.
