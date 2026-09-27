# Dataset independente de atributos técnicos v4

O arquivo `technical-attributes-v4.jsonl` foi congelado antes da primeira medição.

## Objetivo

Medir a generalização das regras técnicas após os ciclos de tuning v1.14, v1.16 e v1.18.

Nenhuma contratação deste conjunto apareceu nos benchmarks técnicos v1, v2 ou v3, nem nos benchmarks de taxonomia v1 a v5.

## Fontes

- Fortaleza/CE, PNCP `07954480000179-1-022500/2026`;
- Piracicaba/SP, PNCP `46341038000129-1-000542/2026`;
- Moema/MG, PNCP `18301044000117-1-000008/2026`;
- Gravataí/RS, PNCP `87890992000158-1-001002/2026`;
- Paranapoema/PR, PNCP `76970391000139-1-000015/2026`;
- Terra Roxa/SP, PNCP `45709896000110-1-000036/2026`;
- Campinas/SP, PNCP `51885242000140-1-000742/2026`;
- Nova Veneza/GO, PNCP `08868932000162-1-000003/2026`.

## Composição

- 45 exemplos;
- 8 contratações inéditas;
- campos positivos e negativos;
- descrições curtas, longas e comerciais;
- rótulos baseados apenas em informação explícita no texto;
- nenhuma alteração de regra entre o congelamento e a primeira medição.

## Casos deliberadamente difíceis

O conjunto inclui:

- `ADESIVO FOTO` como abreviação de fotopolimerização;
- anestésicos com vasoconstritor genérico sem substância nomeada;
- `APINEFRINA` como grafia publicada;
- resina nanoparticulada, ainda sem classe canônica própria;
- menções a `fotopolimerizável` em contexto que não descreve necessariamente o adesivo;
- resina `micro ou nanoparticulada`;
- flúor 1,23% sem declarar se é acidulado ou neutro;
- adesivos de frasco único sem estratégia clínica explícita.

## Regra metodológica

A primeira medição deve ser registrada antes de qualquer tuning.

Se houver erros, o dataset permanece imutável e toda melhoria posterior deve ser publicada em artefato separado.
