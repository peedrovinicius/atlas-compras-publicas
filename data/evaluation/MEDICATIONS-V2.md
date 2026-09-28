# Dataset independente de medicamentos v2

O arquivo `medications-v2.jsonl` foi congelado antes da primeira medição no commit `28ba1d69ac0f518d1aa170c9a99e70a482cdf7b7`.

## Objetivo

Medir a generalização do parser de medicamentos após o tuning da v1.44 em oito contratações ainda não usadas no medicamentos v1.

## Fontes

- Secretaria da Saúde do Ceará, Fortaleza/CE, PNCP `07954480000179-1-020447/2026`;
- Fundo Municipal de Saúde de Aparecida de Goiânia/GO, PNCP `11809185000104-1-000037/2026`;
- Fundo Municipal da Saúde de Gravataí/RS, PNCP `87890992000158-1-000941/2026`;
- Município de Sapezal/MT, PNCP `01614225000109-1-000102/2026`;
- Fundação Hospitalar de Feira de Santana/BA, PNCP `40637159000136-1-000065/2026`;
- Fundo Municipal de Saúde de Volta Redonda/RJ, PNCP `39563911000162-1-000181/2026`;
- Fundação Municipal de Saúde de Teresina/PI, PNCP `05522917000170-1-000156/2026`;
- Município de Cristalina/GO, PNCP `01138122000101-1-000035/2026`.

## Composição

- 48 exemplos;
- 8 contratações inéditas;
- 192 campos revisados;
- seis exemplos por contratação;
- ingredientes isolados e associados;
- sais e qualificadores;
- concentrações em mg, g, UI e razões com volume;
- formas injetável, oftálmica, oral líquida, cápsula e tópica;
- texto colado e abreviações reais.

## Regra metodológica

O parser v1.44 foi validado primeiro contra o medicamentos v1 pós-tuning, reproduzindo 192/192 campos.

Somente depois foi feita a primeira medição do v2.

Nenhuma lacuna do v2 será corrigida na v1.45.
