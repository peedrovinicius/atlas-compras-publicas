# Dataset independente de atributos técnicos v10

O arquivo `technical-attributes-v10.jsonl` foi congelado antes da primeira medição no commit `543fcab93af68ad1a1ed925d8d6d3ba2b20b6e5a`.

## Objetivo

Medir a generalização do parser após o tuning da v1.30 em oito contratações ainda não usadas nos benchmarks técnicos v1 a v9.

## Fontes

- Cachoeira de Minas/MG, PNCP `18675959000192-1-000131/2026`;
- Sumaré/SP, PNCP `45787660000100-1-000282/2026`;
- Ipiranga/PR, PNCP `76175934000126-1-000048/2026`;
- Igaratá/SP, PNCP `46694147000120-1-000074/2026`;
- Mineiros/GO, PNCP `11924138000101-1-000511/2026`;
- 11º Depósito de Suprimentos do Exército/DF, PNCP `00394452000103-1-015128/2026`;
- Contenda/PR, PNCP `76105519000104-1-000193/2026`;
- Francisco Beltrão/PR, PNCP `77816510000166-1-000274/2026`.

## Composição

- 48 exemplos;
- 8 contratações inéditas;
- 84 campos técnicos revisados;
- seis exemplos por contratação;
- descrições curtas e extensas;
- produtos fora da taxonomia que citam termos conhecidos;
- variações de fotopolimerização descritas por linguagem livre;
- produto fluoretado em forma não gel;
- ionômero reforçado por resina;
- conflito explícito entre dois vasoconstritores na mesma descrição.

## Fidelidade da descrição

O conjunto usa trechos fiéis das descrições públicas, preservando o conteúdo técnico necessário para rotulagem.

Foram removidos apenas preço, quantidade, regras de participação e trechos editoriais sem valor técnico.

## Regra metodológica

A primeira medição ocorreu somente após o congelamento do dataset.

O espelho determinístico da v1.30 foi validado antes contra o v9 pós-tuning e reproduziu exatamente:

- 48/48 categorias;
- 84/84 campos técnicos.

Nenhuma lacuna do v10 será corrigida na v1.31. Qualquer tuning posterior deve preservar este dataset e esta baseline.
