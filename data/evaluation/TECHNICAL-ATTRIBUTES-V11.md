# Dataset independente de atributos técnicos v11

O arquivo `technical-attributes-v11.jsonl` foi congelado antes da primeira medição no commit `23749c5987ca9ed681b4cb28a9ce0f24e24649ad`.

## Objetivo

Medir a generalização do parser após o tuning da v1.32 em oito contratações ainda não usadas nos benchmarks técnicos v1 a v10.

## Fontes

- Hortolândia/SP, PNCP `67995027000132-1-000296/2026`;
- José Bonifácio/SP, PNCP `45141132000171-1-000059/2026`;
- Capela do Alto/SP, PNCP `46634077000114-1-000088/2026`;
- Secretaria da Segurança Pública de São Paulo, PNCP `46377800000127-1-003198/2026`;
- Secretaria da Saúde do Ceará, PNCP `07954480000179-1-020992/2026`;
- Consórcio Intermunicipal do Vale do Paranapanema, Assis/SP, PNCP `51501484000193-1-000034/2026`;
- Alcantil/PB, PNCP `01612470000179-1-000004/2026`;
- Santa Maria de Jetibá/ES, PNCP `13917262000167-1-000014/2026`.

## Composição

- 48 exemplos;
- 8 contratações inéditas;
- 80 campos técnicos revisados;
- seis exemplos por contratação;
- descrições muito curtas e descrições longas;
- abreviação `CIV`;
- resina descrita apenas por nome e cor;
- epinefrina truncada;
- revelador descrito apenas como produto para película;
- pontuação inserida entre os termos da identidade;
- óxido de zinco e resinas usados apenas como componentes;
- positivos e negativos contextuais.

## Fidelidade da descrição

O conjunto usa trechos fiéis das descrições públicas.

Foram removidos apenas preços, quantidades, regras de participação e repetições editoriais sem valor técnico. Não foram introduzidas paráfrases para facilitar o parser.

## Regra metodológica

A primeira medição ocorreu somente após o congelamento do dataset.

O espelho determinístico da v1.32 foi validado antes contra o v10 pós-tuning e reproduziu exatamente:

- 48/48 categorias;
- 84/84 campos técnicos.

Nenhuma lacuna do v11 será corrigida na v1.33. Qualquer tuning posterior deve preservar este dataset e esta baseline.
