# Dataset independente de atributos técnicos v7

O arquivo `technical-attributes-v7.jsonl` foi congelado antes da primeira medição.

## Objetivo

Medir a generalização das regras técnicas após o tuning restrito da v1.24.

Nenhuma das oito contratações deste conjunto apareceu nos benchmarks técnicos v1 a v6.

## Fontes

- Baixo Guandu/ES, PNCP `11682696000108-1-000027/2026`;
- Ibiporã/PR, PNCP `76244961000103-1-000091/2026`;
- Hospital Naval de Natal/RN, PNCP `00394502000144-1-011012/2026`;
- Senhora dos Remédios/MG, PNCP `18094870000132-1-000065/2026`;
- Diamante D'Oeste/PR, PNCP `77817476000144-1-000027/2026`;
- Cerro Azul/PR, PNCP `76105626000124-1-000024/2026`;
- Matutina/MG, PNCP `18602102000142-1-000030/2026`;
- Escola de Guerra Naval, Rio de Janeiro/RJ, PNCP `00394502000144-1-011091/2026`.

## Composição

- 48 exemplos;
- 8 contratações inéditas;
- 83 campos técnicos revisados;
- positivos e negativos contextuais;
- produtos comerciais com descrição curta;
- erros ortográficos e variações morfológicas;
- anestésicos tópicos com benzocaína;
- referências subordinadas a adesivo, ionômero, resina e fluoreto;
- nenhuma alteração de regra entre congelamento e primeira medição.

## Casos deliberadamente difíceis

O conjunto inclui:

- adesivo para moldeira com a palavra `universal`, mas que não é adesivo dentário restaurador;
- selante cuja descrição menciona restaurações de ionômero de vidro;
- anestésicos tópicos de benzocaína;
- `decapagem total` como forma de descrever condicionamento total;
- `LONÔMERO DE VIDRO` com erro gráfico;
- `forração` e `restaurações` como variações de uso de ionômero;
- revelador radiográfico descrito apenas como `REVELADOR`;
- resina comercial `FILTEK Z250 XT` sem a expressão `resina composta`;
- cariostático e dessensibilizante contendo fluoreto sem serem classificados como gel de flúor.

## Regra metodológica

A primeira medição foi registrada antes de qualquer tuning.

Os erros desta baseline não serão corrigidos na v1.25. Qualquer melhoria posterior deve manter este dataset e esta baseline imutáveis e registrar o resultado pós-tuning em artefato separado.
