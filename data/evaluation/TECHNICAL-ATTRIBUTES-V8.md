# Dataset independente de atributos técnicos v8

O arquivo `technical-attributes-v8.jsonl` foi congelado antes da primeira medição válida no commit `f126e0332697207b689505b947c48a2c584f5822`.

## Objetivo

Medir a generalização das regras técnicas após o tuning da v1.26 em contratações ainda não usadas nos benchmarks técnicos anteriores.

Nenhum dos oito números de controle PNCP deste conjunto apareceu nos benchmarks técnicos v1 a v7.

## Fontes

- Vera Cruz do Oeste/PR, PNCP `78101821000101-1-000176/2026`;
- Sorocaba/SP, PNCP `46634044000174-1-000116/2026`;
- Policlínica Naval Nossa Senhora da Glória/RJ, PNCP `00394502000144-1-004017/2026`;
- Tribunal Superior Eleitoral/DF, PNCP `00509018000113-1-002227/2026`;
- IFNMG Campus Salinas/MG, PNCP `10727655000110-1-000144/2026`;
- São José do Divino/PI, PNCP `41522111000145-1-000051/2026`;
- Câmara Municipal de Salvador/BA, PNCP `14674402000186-1-000026/2026`;
- Governo do Estado do Ceará, Fortaleza/CE, PNCP `07954480000179-1-021297/2026`.

## Composição

- 48 exemplos;
- 8 contratações inéditas;
- 83 campos técnicos revisados;
- seis exemplos por contratação;
- positivos e negativos contextuais;
- abreviações e descrições comerciais;
- alternativas explícitas ligadas por `ou`;
- referências de marca dentro da descrição;
- materiais que apenas citam adesivo, ionômero, resina, flúor ou eugenol.

## Fidelidade da descrição

O v8 usa trechos curtos e fiéis do campo público de descrição do item.

Foram removidos apenas preço, quantidade, regras de participação e texto editorial da página agregadora. Em descrições muito longas, o trecho preserva a parte técnica inicial necessária para identificar o produto e os atributos revisados.

O conjunto não usa paráfrases semânticas na baseline oficial.

## Regra metodológica

A primeira medição válida ocorreu somente após o congelamento do arquivo final.

O espelho determinístico usado na medição foi validado antes contra o v7 pós-tuning e reproduziu exatamente:

- 48/48 categorias;
- 83/83 campos técnicos.

Nenhuma lacuna do v8 será corrigida na v1.27. Qualquer tuning posterior deve manter este dataset e esta baseline imutáveis e registrar o resultado pós-tuning em artefato separado.
