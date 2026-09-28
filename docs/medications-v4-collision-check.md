# Checagem de colisão do holdout de medicamentos v4

## Objetivo

Registrar a primeira checagem objetiva dos processos candidatos ao holdout independente de medicamentos v4 antes da criação de `data/evaluation/medications-v4.jsonl`.

Esta checagem não congela o dataset. Ela apenas confirma que os processos candidatos não aparecem, por número de controle, nos arquivos já existentes dos benchmarks de medicamentos v1, v2 e v3.

## Escopo verificado

Arquivos de referência:

- `data/evaluation/medications-v1.jsonl`;
- `data/evaluation/medications-v2.jsonl`;
- `data/evaluation/medications-v3.jsonl`.

Critério aplicado nesta etapa:

- busca textual do número de controle candidato no repositório;
- conferência contra os processos conhecidos dos holdouts anteriores;
- marcação como apto apenas para triagem item a item, não para congelamento automático.

## Matriz de candidatos

| Status | Prioridade | Local | Processo candidato | Número de controle candidato | Resultado da checagem por processo |
| --- | --- | --- | --- | --- | --- |
| Apto para triagem | Alta | Fortaleza/CE | PE 327/2026 | `07954480000179-1-023220/2026` | Não encontrado em v1, v2 ou v3 |
| Apto para triagem | Alta | Curitiba/PR | PE 74/2026 | `14814139000183-1-000149/2026` | Não encontrado em v1, v2 ou v3 |
| Apto para triagem | Alta | São Paulo/SP | PE 17/2026 | `46374500000194-1-007776/2026` | Não encontrado em v1, v2 ou v3 |
| Apto para triagem | Alta | Curitiba/PR | PE 48/2026 | `24039073000155-1-001079/2026` | Não encontrado em v1, v2 ou v3 |
| Apto para triagem | Média | Brasília/DF | PE 90018/2026 | `00394411000109-1-000150/2026` | Não encontrado em v1, v2 ou v3 |
| Apto para triagem | Média | Orlândia/SP | PE 92/2026 | `45351749000111-1-000100/2026` | Não encontrado em v1, v2 ou v3 |
| Apto para triagem | Média | São Paulo/SP | PE 246/2026 | `46854998000192-1-000467/2026` | Não encontrado em v1, v2 ou v3 |
| Apto para triagem | Média | Curitiba/PR | PE 10/2026 | `03518900000113-1-000010/2026` | Não encontrado em v1, v2 ou v3 |
| Apto para triagem | Média | Salvador/BA | PE 124/2026 | `13927801000149-1-000171/2026` | Não encontrado em v1, v2 ou v3 |
| Reserva | Baixa | Fortaleza/CE | PE 202621567/2026 | `07954480000179-1-022607/2026` | Não encontrado em v1, v2 ou v3 |
| Reserva | Baixa | Brasília/DF | PE 90052/2026 | `00394544000185-1-001239/2026` | Não encontrado em v1, v2 ou v3 |
| Reserva | Baixa | Fortaleza/CE | PE 475/2026 | `07954480000179-1-024203/2026` | Não encontrado em v1, v2 ou v3 |

## Processos já conhecidos dos ciclos anteriores

A checagem evita repetir os processos usados nos holdouts anteriores. Exemplos de processos já presentes nos datasets congelados incluem:

- medicamentos v1: Campinas/SP `47018676000176-1-000364/2026`;
- medicamentos v1: Varginha/MG `19110162000100-1-000212/2026`;
- medicamentos v1: Montividiu/GO `11269276000196-1-000008/2026`;
- medicamentos v1: Botucatu/SP `12474705000120-1-000254/2026`;
- medicamentos v2: Fortaleza/CE `07954480000179-1-020447/2026`;
- medicamentos v2: Aparecida de Goiânia/GO `11809185000104-1-000037/2026`;
- medicamentos v2: Gravataí/RS `87890992000158-1-000941/2026`;
- medicamentos v2: Sapezal/MT `01614225000109-1-000102/2026`;
- medicamentos v3: Fortaleza/CE `07954605000160-1-000893/2026`;
- medicamentos v3: Fortaleza/CE `07954605000160-1-000874/2026`;
- medicamentos v3: Ariquemes/RO `04104816000116-1-000212/2026`;
- medicamentos v3: Brasília/DF `00394502000144-1-010691/2026`.

## Resultado

A primeira seleção possui processos suficientes para iniciar a triagem item a item sem repetir número de controle PNCP dos ciclos v1, v2 e v3.

A seleção inicial recomendada permanece:

1. Fortaleza/CE — PE 327/2026;
2. Curitiba/PR — PE 74/2026;
3. São Paulo/SP — PE 17/2026;
4. Curitiba/PR — PE 48/2026;
5. Brasília/DF — PE 90018/2026;
6. Orlândia/SP — PE 92/2026;
7. São Paulo/SP — PE 246/2026;
8. Salvador/BA — PE 124/2026.

O processo Curitiba/PR PE 10/2026 fica como candidato alternativo por conter grafia problemática, mas não deve entrar na primeira leva se os oito grupos acima forem suficientes.

## Próxima etapa obrigatória

Antes de criar `medications-v4.jsonl`, selecionar 6 itens por processo e aplicar uma segunda checagem:

- descrição idêntica contra v1, v2 e v3;
- descrição quase idêntica contra v1, v2 e v3;
- repetição excessiva de princípio ativo já usado;
- diversidade entre concentração, forma farmacêutica e via;
- descarte de itens que dependam de inferência manual excessiva.

Somente após essa segunda checagem o dataset v4 poderá ser congelado.
