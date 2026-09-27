# Dataset independente de atributos técnicos v9

O arquivo `technical-attributes-v9.jsonl` foi congelado antes da primeira medição no commit `1f03ffbb9eacabdd6076c7b5b378fa05910ea78c`.

## Objetivo

Medir a generalização do parser após o tuning da v1.28 em oito contratações ainda não usadas nos benchmarks técnicos v1 a v8.

## Fontes

- Barrocas/BA, PNCP `04216287000142-1-000060/2026`;
- Colorado/RS, PNCP `87613527000170-1-000099/2026`;
- Lagoa de Itaenga/PE, PNCP `11097250000108-1-000102/2026`;
- Comando da Aeronáutica, Recife/PE, PNCP `00394429000100-1-002354/2026`;
- Corpo de Bombeiros/RJ, PNCP `42498600000171-1-003854/2026`;
- Guaraci/PR, PNCP `75845537000151-1-000095/2026`;
- Barra Bonita/SP, PNCP `46172888000140-1-000262/2026`;
- Universidade Federal do Espírito Santo, PNCP `32479123000143-1-000143/2026`.

## Composição

- 48 exemplos;
- 8 contratações inéditas;
- 84 campos técnicos revisados;
- seis exemplos por contratação;
- descrições comerciais curtas;
- pontuação interna em nomes de produto;
- composição subordinada que não define o produto principal;
- grafia imperfeita de vasoconstritor;
- forma explícita sem vasoconstritor;
- materiais restauradores e anestésicos com variações reais de linguagem.

## Fidelidade da descrição

O conjunto usa trechos curtos e fiéis dos campos públicos de descrição.

Foram removidos apenas preço, quantidade, regras de participação e repetições editoriais sem valor técnico. Não foram introduzidas paráfrases para corrigir ou facilitar a interpretação do parser.

## Regra metodológica

A primeira medição ocorreu somente após o congelamento do dataset.

O espelho determinístico da v1.28 foi validado antes contra o v8 pós-tuning e reproduziu exatamente:

- 48/48 categorias;
- 83/83 campos técnicos.

Nenhuma lacuna do v9 será corrigida na v1.29. Qualquer tuning posterior deve preservar este dataset e esta baseline.
