# Dataset independente de atributos técnicos v6

O arquivo `technical-attributes-v6.jsonl` foi congelado antes da primeira medição.

## Objetivo

Medir a generalização das regras técnicas após o tuning contextual da v1.22.

Nenhuma contratação deste conjunto apareceu nos benchmarks técnicos v1 a v5 ou nos benchmarks de taxonomia v1 a v5.

## Fontes

- Lagoa do Carro/PE, PNCP `11326603000102-1-000030/2026`;
- Universidade Federal do Espírito Santo, PNCP `32479123000143-1-000148/2026`;
- Ponta Grossa/PR, PNCP `76175884000187-1-000388/2026`;
- Piraquara/PR, PNCP `76105675000167-1-000075/2026`;
- Serra/ES, PNCP `27174093000127-1-000260/2026`;
- Comando do Exército, Curitiba/PR, PNCP `00394452000103-1-018839/2026`;
- UFVJM, Diamantina/MG, PNCP `16888315000157-1-000018/2026`;
- Universidade Federal do Paraná, PNCP `75095679000149-1-000481/2026`.

## Composição

- 48 exemplos;
- 8 contratações inéditas;
- campos positivos e negativos;
- itens genéricos sem atributo técnico explícito;
- referências subordinadas a resina que não representam resina restauradora;
- anestésicos com e sem vasoconstritor nomeado;
- flúor em gel e fluoreto em solução;
- adesivo com ativação dual e estratégia autocondicionante;
- nenhuma alteração de regra entre congelamento e primeira medição.

## Casos deliberadamente difíceis

O conjunto inclui:

- `Fluoreto De Sódio` em gel e em solução bucal;
- `Prilocaína` sem a palavra anestésico;
- `resina acrílica` em dentes artificiais e acessórios;
- `resinas termoplásticas` em sugadores;
- ionômero descrito como resinoso;
- selantes fotopolimerizáveis que não são resina composta;
- adesivo dual autocondicionante.

## Regra metodológica

A primeira medição deve ser registrada antes de qualquer tuning.

Se houver erros, o dataset permanece imutável e toda melhoria posterior deve ser publicada em artefato separado.
