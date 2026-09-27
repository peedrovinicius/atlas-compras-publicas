# Dataset independente de atributos técnicos v5

O arquivo `technical-attributes-v5.jsonl` foi congelado antes da primeira medição.

## Objetivo

Medir a generalização das regras técnicas após a introdução de contexto negativo na v1.20.

Nenhuma contratação deste conjunto apareceu nos benchmarks técnicos v1 a v4 ou nos benchmarks de taxonomia v1 a v5.

## Fontes

- Votorantim/SP, PNCP `46634051000176-1-000153/2026`;
- Junqueirópolis/SP, PNCP `44881449000181-1-000128/2026`;
- Braga/RS, PNCP `87613170000120-1-000075/2026`;
- Cássia dos Coqueiros/SP, PNCP `44229805000187-1-000064/2026`;
- São Mateus/ES, PNCP `11356696000100-1-000050/2026`;
- Conceição da Aparecida/MG, PNCP `18243295000192-1-000065/2026`;
- Poço de José de Moura/PB, PNCP `01615784000125-1-000036/2026`;
- Rialma/GO, PNCP `10459591000113-1-000057/2026`.

## Composição

- 48 exemplos;
- 8 contratações inéditas;
- campos positivos e negativos;
- erros de digitação presentes nas fontes;
- referências comerciais;
- alternativas técnicas explícitas;
- negativos contextuais;
- nenhum ajuste de regra entre o congelamento e a primeira medição.

## Casos deliberadamente difíceis

O conjunto inclui:

- `FOTOPOLIMERIZALVEL` e `FOTOPOLIMERIXAVE`;
- `MICROHIDRIDA`;
- `APLICADOR DE ADESIVO`, que não é adesivo;
- brocas e pontas para acabamento de resina, que não são resina;
- selante que menciona `RESINA FOTOPOLIMERIZÁVEL`, sem ser uma resina restauradora;
- `MICRO-HIBRIDA OU NANO-HIBRIDA`, em que não existe uma tecnologia única definida;
- `RESINA FOTO` como abreviação comercial;
- `RESINA ODONTOLÓGICA` sem a expressão `resina composta`;
- anestésico com princípio ativo explícito, mas sem vasoconstritor nomeado.

## Regra metodológica

A primeira medição deve ser registrada antes de qualquer tuning.

Se houver erros, o dataset permanece imutável e toda melhoria posterior deve ser publicada em artefato separado.
