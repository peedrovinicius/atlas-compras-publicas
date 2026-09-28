# Congelamento do holdout de medicamentos v4

## Status

O arquivo `data/evaluation/medications-v4.jsonl` foi criado e congelado como novo holdout independente do domínio de medicamentos.

Este congelamento fecha a etapa de construção do dataset. Nenhum ajuste do parser foi feito antes da criação do arquivo.

## Identificação

| Campo | Valor |
| --- | --- |
| Dataset | `medications-v4.jsonl` |
| Caminho | `data/evaluation/medications-v4.jsonl` |
| Commit de congelamento | `152c82c8a91737f897cfc251f07f376ea76ee4ed` |
| Blob SHA GitHub | `ef7561d060cdf578529690391da184ac55a02143` |
| SHA-256 do conteúdo | `2c50bb9f9695b3594d2b6a3d74c22483320e296faabf80964f365f3062142976` |
| Status | congelado para baseline independente |

## Composição

| Métrica | Valor |
| --- | ---: |
| Exemplos | 48 |
| Campos avaliados por exemplo | 4 |
| Campos esperados revisados | 192 |
| Fontes públicas | 8 |
| Parser alterado antes do congelamento | não |

## Fontes usadas

| Fonte | Controle PNCP | Exemplos |
| --- | --- | ---: |
| Curitiba/PR PE 93/2026 | `14814139000183-1-000142/2026` | 30 |
| Brasília/DF PE 90018/2026 | `00394411000109-1-000150/2026` | 9 |
| Curitiba/PR PE 74/2026 | `14814139000183-1-000149/2026` | 2 |
| São Paulo/SP PE 33/2026 | `46374500000194-1-007596/2026` | 1 |
| Curitiba/PR PE 1270/2026 | `24039073000155-1-001089/2026` | 1 |
| Santos/SP PE 21/2026 | `46374500000194-1-006714/2026` | 2 |
| Curitiba/PR PE 87/2026 | `14814139000183-1-000136/2026` | 2 |
| Curitiba/PR PE 84/2026 | `14814139000183-1-000132/2026` | 1 |

## Decisão metodológica

O plano inicial previa 8 contratações com 6 itens por contratação. Durante a triagem, a seleção foi ajustada para preservar apenas descrições verificáveis nas fontes públicas abertas.

A regra adotada no congelamento foi:

1. manter 48 exemplos;
2. manter 192 campos avaliados;
3. usar apenas fontes públicas com descrição suficiente;
4. não completar descrições por inferência fraca;
5. não alterar o parser antes da primeira medição.

Essa decisão preserva a validade do holdout: é preferível um conjunto congelado com distribuição desigual entre fontes, mas com descrições verificáveis, do que forçar 6 itens por fonte usando dados incompletos.

## Revisão manual dos campos

Foram revisados os quatro campos esperados de cada exemplo:

- princípio ativo;
- concentração;
- forma farmacêutica;
- via de administração.

Valores ausentes na própria descrição foram mantidos como `null` ou `unknown`, conforme o contrato do avaliador.

## Próxima etapa

A próxima ação é executar o parser vigente contra `data/evaluation/medications-v4.jsonl` e registrar a baseline independente em `data/evaluation/medications-v4-baseline.json`.

Somente depois da baseline documentada poderá haver decisão sobre eventual tuning posterior.
