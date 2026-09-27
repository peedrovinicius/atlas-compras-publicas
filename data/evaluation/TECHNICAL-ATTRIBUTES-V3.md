# Dataset independente de atributos técnicos v3

O arquivo `technical-attributes-v3.jsonl` foi congelado antes da primeira medição.

## Objetivo

Medir a generalização das regras técnicas após os ciclos de tuning v1.14 e v1.16.

Nenhuma contratação deste conjunto foi usada nos benchmarks técnicos v1 ou v2, nem nos benchmarks de taxonomia v1 a v5.

## Fontes

- Messias Targino/RN, PNCP `08349060000126-1-000008/2026`;
- Tio Hugo/RS, PNCP `04207638000159-1-000070/2026`;
- Natal/RN, PNCP `05792645000128-1-000046/2026`;
- Itabaiana/PB, PNCP `09072430000193-1-000071/2026`;
- Salgueiro/PE, PNCP `11361243000171-1-000195/2026`;
- Cruzália/SP, PNCP `46179966000139-1-000014/2026`;
- Guaratinguetá/SP, PNCP `00394429000100-1-002037/2026`;
- Aparecida do Rio Doce/GO, PNCP `24859316000100-1-000245/2026`.

## Composição

- 45 exemplos;
- 8 contratações inéditas;
- descrições curtas e extensas;
- abreviações e erros de grafia presentes nas fontes;
- campos positivos e negativos;
- rótulos baseados apenas em informação explícita da descrição;
- nenhum ajuste de regra entre o congelamento e a primeira medição.

## Casos deliberadamente difíceis

A amostra inclui, entre outros:

- `S/VASOCONSTR.`;
- `SEM VASOCONTRITOR`;
- `FOTOATIVADO`;
- resina descrita apenas como `RESINA BULK FILL`;
- resinas no plural;
- ionômeros sem indicação de uso;
- fluoreto de sódio sem dizer explicitamente `acidulado` ou `neutro`;
- resina nanoparticulada, tecnologia ainda não representada no vocabulário canônico.

## Regra metodológica

A primeira medição deve ser registrada antes de qualquer tuning.

Se houver erros, o dataset permanece imutável e toda melhoria posterior deve ser publicada em artefato separado.
